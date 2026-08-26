"""Explicit pipeline gates with no publishing operation."""

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, SkipValidation, model_validator

from channel2.models import Channel, QcStatus, StoryRecord, VerificationStatus


class PipelineStage(StrEnum):
    IDEA = "IDEA"
    PROFILE_VALIDATED = "PROFILE_VALIDATED"
    RESEARCH_COMPLETE = "RESEARCH_COMPLETE"
    STORY_READY = "STORY_READY"
    SCRIPT_READY = "SCRIPT_READY"
    PRODUCTION_PLANNED = "PRODUCTION_PLANNED"
    MEDIA_ASSEMBLED = "MEDIA_ASSEMBLED"
    QC_COMPLETE = "QC_COMPLETE"
    DRAFT_READY_FOR_HUMAN = "DRAFT_READY_FOR_HUMAN"


class PipelineGateError(ValueError):
    """Raised when a record attempts to bypass a required stage gate."""


_NEXT_STAGE: dict[PipelineStage, PipelineStage] = {
    PipelineStage.IDEA: PipelineStage.PROFILE_VALIDATED,
    PipelineStage.PROFILE_VALIDATED: PipelineStage.RESEARCH_COMPLETE,
    PipelineStage.RESEARCH_COMPLETE: PipelineStage.STORY_READY,
    PipelineStage.STORY_READY: PipelineStage.SCRIPT_READY,
    PipelineStage.SCRIPT_READY: PipelineStage.PRODUCTION_PLANNED,
    PipelineStage.PRODUCTION_PLANNED: PipelineStage.MEDIA_ASSEMBLED,
    PipelineStage.MEDIA_ASSEMBLED: PipelineStage.QC_COMPLETE,
    PipelineStage.QC_COMPLETE: PipelineStage.DRAFT_READY_FOR_HUMAN,
}


class Pipeline(BaseModel):
    """State machine whose terminal automated state requires human review.

    The channel is supplied explicitly rather than looked up, so a record can
    never be advanced under a policy other than its own channel's.
    """

    model_config = ConfigDict(validate_assignment=True)

    # Validation is skipped deliberately. Pydantic re-runs a nested model's
    # validators even for an already-valid instance, which would re-resolve the
    # record's channel against the packaged registry and discard the registry
    # the record was actually validated under. The record arrives valid; the
    # channel it runs under is passed explicitly rather than re-derived.
    record: SkipValidation[StoryRecord]
    channel: Channel
    stage: PipelineStage = PipelineStage.IDEA

    @model_validator(mode="after")
    def validate_channel_matches_record(self) -> "Pipeline":
        if not isinstance(self.record, StoryRecord):
            raise ValueError(
                f"record must be a StoryRecord, not {type(self.record).__name__}"
            )
        if self.channel.channel_id != self.record.channel_id:
            raise ValueError(
                f"pipeline channel '{self.channel.channel_id}' does not match "
                f"record channel '{self.record.channel_id}'"
            )
        return self

    def advance(self, target: PipelineStage) -> None:
        if not self.channel.active:
            raise PipelineGateError(
                f"channel '{self.channel.channel_id}' is retired; its records "
                "stay readable but cannot enter production"
            )
        expected = _NEXT_STAGE.get(self.stage)
        if expected is None:
            raise PipelineGateError(
                "the automated pipeline stops at DRAFT_READY_FOR_HUMAN"
            )
        if target != expected:
            raise PipelineGateError(
                f"cannot advance from {self.stage} to {target}; expected {expected}"
            )
        self._check_gate(target)
        self.stage = target

    def _check_gate(self, target: PipelineStage) -> None:
        if target == PipelineStage.RESEARCH_COMPLETE:
            classification = self.record.classification
            if self.channel.verification_policy.requires_verification(
                classification
            ) and self.record.verification_status not in {
                VerificationStatus.PARTIALLY_VERIFIED,
                VerificationStatus.VERIFIED,
            }:
                raise PipelineGateError(
                    f"{classification.value} research for channel "
                    f"'{self.channel.channel_id}' is not sufficiently verified"
                )
        elif target == PipelineStage.SCRIPT_READY and not self.record.script:
            raise PipelineGateError("a script is required")
        elif target == PipelineStage.PRODUCTION_PLANNED:
            if not self.record.timeline_path:
                raise PipelineGateError("a production timeline is required")
        elif target == PipelineStage.MEDIA_ASSEMBLED:
            if not self.record.draft_path:
                raise PipelineGateError("a draft path is required")
        elif target == PipelineStage.QC_COMPLETE:
            if self.record.qc_status == QcStatus.NOT_STARTED:
                raise PipelineGateError("quality control has not run")
        elif target == PipelineStage.DRAFT_READY_FOR_HUMAN:
            if self.record.qc_status != QcStatus.PASSED:
                raise PipelineGateError("only a draft that passed QC can reach review")
