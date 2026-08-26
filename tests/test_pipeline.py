"""Fail-closed pipeline stage-gate tests."""

import pytest

from channel2.knowledge import ChannelRegistry
from channel2.models import QcStatus, StoryRecord, VerificationStatus
from channel2.pipeline import Pipeline, PipelineGateError, PipelineStage
from conftest import TEST_ONLY_CHANNEL_ID, context_for

_TO_HUMAN_REVIEW = (
    PipelineStage.PROFILE_VALIDATED,
    PipelineStage.RESEARCH_COMPLETE,
    PipelineStage.STORY_READY,
    PipelineStage.SCRIPT_READY,
    PipelineStage.PRODUCTION_PLANNED,
    PipelineStage.MEDIA_ASSEMBLED,
    PipelineStage.QC_COMPLETE,
    PipelineStage.DRAFT_READY_FOR_HUMAN,
)


def _pipeline_for(record: StoryRecord, registry: ChannelRegistry) -> Pipeline:
    return Pipeline(record=record, channel=registry.get(record.channel_id))


def test_cannot_skip_pipeline_stages(
    roblox_record: StoryRecord, test_registry: ChannelRegistry
) -> None:
    pipeline = _pipeline_for(roblox_record, test_registry)
    with pytest.raises(PipelineGateError, match="expected PROFILE_VALIDATED"):
        pipeline.advance(PipelineStage.STORY_READY)


def test_pipeline_refuses_a_channel_the_record_does_not_name(
    roblox_record: StoryRecord, test_registry: ChannelRegistry
) -> None:
    with pytest.raises(ValueError, match="does not match record channel"):
        Pipeline(
            record=roblox_record,
            channel=test_registry.get(TEST_ONLY_CHANNEL_ID),
        )


def test_pipeline_ends_at_human_review(test_registry: ChannelRegistry) -> None:
    record = StoryRecord.model_validate(
        {
            "channel_id": TEST_ONLY_CHANNEL_ID,
            "story_id": "STORY-TEST-3",
            "title": "A documented survival event",
            "premise": "A survivor recounts a documented animal encounter.",
            "classification": "nonfiction",
            "content_pillar": "mystery-strange",
            "story_mode": "survival",
            "emotions": ["shock", "relief"],
            "verification_status": "verified",
            "script": "A verified script.",
            "timeline_path": "data/stories/STORY-TEST-3/timeline.json",
            "draft_path": "data/stories/STORY-TEST-3/draft.mp4",
            "qc_status": "passed",
        },
        context=context_for(test_registry),
    )
    pipeline = _pipeline_for(record, test_registry)
    for stage in _TO_HUMAN_REVIEW:
        pipeline.advance(stage)

    assert pipeline.stage == PipelineStage.DRAFT_READY_FOR_HUMAN
    assert not hasattr(pipeline, "publish")
    with pytest.raises(PipelineGateError, match="stops"):
        pipeline.advance(PipelineStage.DRAFT_READY_FOR_HUMAN)


def test_failed_qc_never_reaches_human_ready(
    roblox_record: StoryRecord, test_registry: ChannelRegistry
) -> None:
    record = roblox_record.model_copy(
        update={
            "script": "A fictional script.",
            "timeline_path": "timeline.json",
            "draft_path": "draft.mp4",
            "qc_status": QcStatus.FAILED,
        }
    )
    pipeline = Pipeline(
        record=record,
        channel=test_registry.get(record.channel_id),
        stage=PipelineStage.QC_COMPLETE,
    )

    with pytest.raises(PipelineGateError, match="passed QC"):
        pipeline.advance(PipelineStage.DRAFT_READY_FOR_HUMAN)


def test_verification_threshold_is_unchanged(test_registry: ChannelRegistry) -> None:
    # Partially verified remains sufficient; researching does not.
    def record_with(status: VerificationStatus) -> StoryRecord:
        return StoryRecord.model_validate(
            {
                "channel_id": TEST_ONLY_CHANNEL_ID,
                "story_id": "STORY-TEST-4",
                "title": "A partially supported account",
                "premise": "Some claims are supported and some are not.",
                "classification": "nonfiction",
                "content_pillar": "mystery-strange",
                "story_mode": "mystery-discovery",
                "emotions": ["curiosity"],
                "verification_status": status.value,
            },
            context=context_for(test_registry),
        )

    passing = _pipeline_for(
        record_with(VerificationStatus.PARTIALLY_VERIFIED), test_registry
    )
    passing.advance(PipelineStage.PROFILE_VALIDATED)
    passing.advance(PipelineStage.RESEARCH_COMPLETE)

    blocked = _pipeline_for(record_with(VerificationStatus.RESEARCHING), test_registry)
    blocked.advance(PipelineStage.PROFILE_VALIDATED)
    with pytest.raises(PipelineGateError, match="not sufficiently verified"):
        blocked.advance(PipelineStage.RESEARCH_COMPLETE)
