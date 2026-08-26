"""Shared test records."""

import pytest

from channel2.models import StoryRecord


@pytest.fixture
def fiction_record() -> StoryRecord:
    return StoryRecord.model_validate(
        {
            "story_id": "STORY-TEST-1",
            "title": "The door in the forest",
            "premise": "A fictional hiker finds an impossible door.",
            "classification": "fiction",
            "content_pillar": "mystery-strange",
            "story_mode": "mystery-discovery",
            "emotions": ["curiosity"],
            "verification_status": "not-required",
        }
    )


@pytest.fixture
def nonfiction_record() -> StoryRecord:
    return StoryRecord.model_validate(
        {
            "story_id": "STORY-TEST-2",
            "title": "A documented survival event",
            "premise": "A survivor recounts a documented animal encounter.",
            "classification": "nonfiction",
            "content_pillar": "unbelievable-survival",
            "story_mode": "survival",
            "emotions": ["shock", "relief"],
            "verification_status": "unverified",
        }
    )
