"""StoryRecord contract tests."""

import pytest
from pydantic import ValidationError

from channel2.models import HookOption, StoryRecord


def test_story_record_round_trip(roblox_record: StoryRecord) -> None:
    restored = StoryRecord.model_validate_json(roblox_record.model_dump_json())
    assert restored == roblox_record
    assert restored.schema_version == "2.0"
    assert restored.channel_id == "robloxtales"


def test_record_must_name_a_channel() -> None:
    payload = {
        "story_id": "STORY-3",
        "title": "A story with no home",
        "premise": "Nobody said which channel this belongs to.",
        "classification": "fiction",
        "content_pillar": "mystery",
        "story_mode": "twist",
        "emotions": ["surprise"],
        "verification_status": "not-required",
    }
    with pytest.raises(ValidationError, match="channel_id"):
        StoryRecord.model_validate(payload)


def test_selected_hook_must_be_an_option(roblox_record: StoryRecord) -> None:
    payload = roblox_record.model_dump()
    payload["selected_hook"] = HookOption(
        text="A hook that was not proposed", category="curiosity"
    )
    with pytest.raises(ValidationError, match="selected_hook"):
        StoryRecord.model_validate(payload)


def test_hook_category_must_be_a_known_hook_type() -> None:
    with pytest.raises(ValidationError):
        HookOption(text="An opening line", category="vibes")


def test_emotions_must_be_known_targets(roblox_record: StoryRecord) -> None:
    payload = roblox_record.model_dump()
    payload["emotions"] = ["nostalgia"]

    with pytest.raises(ValidationError):
        StoryRecord.model_validate(payload)


def test_story_structure_is_not_a_record_field(roblox_record: StoryRecord) -> None:
    assert "story_structure" not in StoryRecord.model_fields

    payload = roblox_record.model_dump()
    payload["story_structure"] = "calm-tension-relief"
    with pytest.raises(ValidationError):
        StoryRecord.model_validate(payload)
