"""StoryRecord contract tests."""

import pytest
from pydantic import ValidationError

from channel2.models import HookOption, StoryRecord


def test_story_record_round_trip(fiction_record: StoryRecord) -> None:
    restored = StoryRecord.model_validate_json(fiction_record.model_dump_json())
    assert restored == fiction_record
    assert restored.schema_version == "1.0"


def test_nonfiction_requires_verification_state() -> None:
    with pytest.raises(ValidationError, match="nonfiction cannot use"):
        StoryRecord.model_validate(
            {
                "story_id": "STORY-3",
                "title": "Unsupported event",
                "premise": "A claim presented as fact.",
                "classification": "nonfiction",
                "content_pillar": "human-stories",
                "story_mode": "twist",
                "emotions": ["surprise"],
                "verification_status": "not-required",
            }
        )


def test_fiction_cannot_claim_research_verification() -> None:
    with pytest.raises(ValidationError, match="fiction and reality-inspired"):
        StoryRecord.model_validate(
            {
                "story_id": "STORY-4",
                "title": "Invented event",
                "premise": "A fictional story.",
                "classification": "fiction",
                "content_pillar": "human-stories",
                "story_mode": "emotional",
                "emotions": ["warmth"],
                "verification_status": "verified",
            }
        )


def test_selected_hook_must_be_an_option(fiction_record: StoryRecord) -> None:
    payload = fiction_record.model_dump()
    payload["selected_hook"] = HookOption(
        text="A hook that was not proposed", category="curiosity"
    )
    with pytest.raises(ValidationError, match="selected_hook"):
        StoryRecord.model_validate(payload)


def test_hook_category_must_be_a_known_hook_type() -> None:
    with pytest.raises(ValidationError):
        HookOption(text="An opening line", category="vibes")


def test_emotions_must_be_known_targets(fiction_record: StoryRecord) -> None:
    payload = fiction_record.model_dump()
    payload["emotions"] = ["nostalgia"]

    with pytest.raises(ValidationError):
        StoryRecord.model_validate(payload)


def test_story_structure_is_not_a_record_field(fiction_record: StoryRecord) -> None:
    assert "story_structure" not in StoryRecord.model_fields

    payload = fiction_record.model_dump()
    payload["story_structure"] = "calm-tension-relief"
    with pytest.raises(ValidationError):
        StoryRecord.model_validate(payload)
