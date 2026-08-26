"""Explicit pipeline gates with no publishing operation."""

from enum import StrEnum

from pydantic import BaseModel, ConfigDict

from channel2.models import QcStatus, StoryClassification, StoryRecord, VerificationStatus


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
    """State machine whose terminal automated state requires human review."""

    model_config = ConfigDict(validate_assignment=True)

    record: StoryRecord
    stage: PipelineStage = PipelineStage.IDEA

    def advance(self, target: PipelineStage) -> None:
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
            if (
                self.record.classification == StoryClassification.NONFICTION
                and self.record.verification_status
                not in {
                    VerificationStatus.PARTIALLY_VERIFIED,
                    VerificationStatus.VERIFIED,
                }
            ):
                raise PipelineGateError(
                    "nonfiction research is not sufficiently verified"
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
