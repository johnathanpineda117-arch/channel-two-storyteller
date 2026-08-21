"""Honest capability ledger for the currently shipped system."""

from enum import StrEnum


class CapabilityStatus(StrEnum):
    IMPLEMENTED = "IMPLEMENTED"
    TESTED = "TESTED"
    PLANNED = "PLANNED"
    EXPERIMENTAL = "EXPERIMENTAL"
    FUTURE_CONCEPTUAL = "FUTURE/CONCEPTUAL"
    NOT_IMPLEMENTED = "NOT IMPLEMENTED"


# TESTED means an automated test exercises the capability in this repository.
CAPABILITIES: dict[str, CapabilityStatus] = {
    "configuration": CapabilityStatus.TESTED,
    "story_record_schema": CapabilityStatus.TESTED,
    "knowledge_catalog": CapabilityStatus.TESTED,
    "pipeline_stage_gates": CapabilityStatus.TESTED,
    "profile_cli": CapabilityStatus.TESTED,
    "research_and_trend_intelligence": CapabilityStatus.PLANNED,
    "hook_and_story_generation": CapabilityStatus.PLANNED,
    "script_generation": CapabilityStatus.PLANNED,
    "storyboarding": CapabilityStatus.PLANNED,
    "narration": CapabilityStatus.NOT_IMPLEMENTED,
    "video_assembly": CapabilityStatus.NOT_IMPLEMENTED,
    "automated_quality_control": CapabilityStatus.NOT_IMPLEMENTED,
    "human_review_interface": CapabilityStatus.PLANNED,
    "analytics_ingestion": CapabilityStatus.PLANNED,
    "experiment_engine": CapabilityStatus.PLANNED,
    "autonomous_publishing": CapabilityStatus.NOT_IMPLEMENTED,
    "ai_video_generation": CapabilityStatus.EXPERIMENTAL,
    "continuous_multiplatform_monitoring": CapabilityStatus.FUTURE_CONCEPTUAL,
}


def capability_rows() -> list[tuple[str, CapabilityStatus]]:
    """Return stable, alphabetized status rows for CLI or documentation use."""

    return sorted(CAPABILITIES.items())
