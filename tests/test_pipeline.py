"""Fail-closed pipeline stage-gate tests."""

import pytest

from channel2.models import QcStatus, StoryRecord, VerificationStatus
from channel2.pipeline import Pipeline, PipelineGateError, PipelineStage


def test_cannot_skip_pipeline_stages(fiction_record: StoryRecord) -> None:
    pipeline = Pipeline(record=fiction_record)
    with pytest.raises(PipelineGateError, match="expected PROFILE_VALIDATED"):
        pipeline.advance(PipelineStage.STORY_READY)


def test_unverified_nonfiction_stops_at_research(
    nonfiction_record: StoryRecord,
) -> None:
    pipeline = Pipeline(record=nonfiction_record)
    pipeline.advance(PipelineStage.PROFILE_VALIDATED)

    with pytest.raises(PipelineGateError, match="not sufficiently verified"):
        pipeline.advance(PipelineStage.RESEARCH_COMPLETE)


def test_pipeline_ends_at_human_review(nonfiction_record: StoryRecord) -> None:
    record = nonfiction_record.model_copy(
        update={
            "verification_status": VerificationStatus.VERIFIED,
            "script": "A verified script.",
            "timeline_path": "data/stories/STORY-TEST-2/timeline.json",
            "draft_path": "data/stories/STORY-TEST-2/draft.mp4",
            "qc_status": QcStatus.PASSED,
        }
    )
    pipeline = Pipeline(record=record)
    for stage in (
        PipelineStage.PROFILE_VALIDATED,
        PipelineStage.RESEARCH_COMPLETE,
        PipelineStage.STORY_READY,
        PipelineStage.SCRIPT_READY,
        PipelineStage.PRODUCTION_PLANNED,
        PipelineStage.MEDIA_ASSEMBLED,
        PipelineStage.QC_COMPLETE,
        PipelineStage.DRAFT_READY_FOR_HUMAN,
    ):
        pipeline.advance(stage)

    assert pipeline.stage == PipelineStage.DRAFT_READY_FOR_HUMAN
    assert not hasattr(pipeline, "publish")
    with pytest.raises(PipelineGateError, match="stops"):
        pipeline.advance(PipelineStage.DRAFT_READY_FOR_HUMAN)


def test_failed_qc_never_reaches_human_ready(fiction_record: StoryRecord) -> None:
    record = fiction_record.model_copy(
        update={
            "script": "A fictional script.",
            "timeline_path": "timeline.json",
            "draft_path": "draft.mp4",
            "qc_status": QcStatus.FAILED,
        }
    )
    pipeline = Pipeline(record=record, stage=PipelineStage.QC_COMPLETE)

    with pytest.raises(PipelineGateError, match="passed QC"):
        pipeline.advance(PipelineStage.DRAFT_READY_FOR_HUMAN)
