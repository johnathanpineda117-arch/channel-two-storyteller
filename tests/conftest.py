"""Shared test records and the injected test-only channel registry."""

from typing import Any

import pytest

from channel2.knowledge import (
    CHANNEL_REGISTRY_CONTEXT_KEY,
    ChannelRegistry,
    load_channels,
)
from channel2.models import (
    Channel,
    ContentPillar,
    StoryClassification,
    StoryRecord,
    VerificationPolicy,
)

# A channel that requires verification and is still in production. No such
# channel is registered in the packaged registry, and none should be invented
# there: the only real verification-required configuration we have is the
# retired legacy one. This fixture exists solely so the verification-required
# path can be exercised, and is injected per call rather than registered.
TEST_ONLY_CHANNEL_ID = "test-only-verified-claims"

_TEST_ONLY_SOURCE = "tests/conftest.py (test-only fixture; not a real channel)"

# Chosen so the isolation tests have all three cases available:
#   mystery-strange   belongs to this channel and the legacy one, never Roblox
#   unexpected-twist  shared with RobloxTales by explicit declaration, which
#                     lets a payload differ only by channel_id
# robux is deliberately absent, giving a RobloxTales-only pillar to leak-test.
_TEST_ONLY_PILLARS = frozenset(
    {ContentPillar.MYSTERY_STRANGE, ContentPillar.UNEXPECTED_TWIST}
)

VERIFICATION_REQUIRED = VerificationPolicy(
    allowed_classifications={
        StoryClassification.NONFICTION,
        StoryClassification.REALITY_INSPIRED,
    },
    verification_required_for={
        StoryClassification.NONFICTION,
        StoryClassification.REALITY_INSPIRED,
    },
)

VERIFICATION_NOT_REQUIRED = VerificationPolicy(
    allowed_classifications={
        StoryClassification.NONFICTION,
        StoryClassification.REALITY_INSPIRED,
    },
)

# RobloxTales, but demanding verification for everything it publishes. Used to
# prove that changing one channel's policy leaves other channels untouched.
ROBLOX_VERIFICATION_REQUIRED = VerificationPolicy(
    allowed_classifications={
        StoryClassification.FICTION,
        StoryClassification.REALITY_INSPIRED,
    },
    verification_required_for={
        StoryClassification.FICTION,
        StoryClassification.REALITY_INSPIRED,
    },
)


def build_registry(
    *,
    roblox_policy: VerificationPolicy | None = None,
    test_only_policy: VerificationPolicy | None = None,
) -> ChannelRegistry:
    """The packaged channels plus the test-only channel, with optional edits.

    Building a new registry rather than mutating a shared one keeps every test
    independent of every other.
    """

    channels: list[Channel] = []
    for channel in load_channels().channels:
        if channel.channel_id == "robloxtales" and roblox_policy is not None:
            channel = channel.model_copy(
                update={"verification_policy": roblox_policy}
            )
        channels.append(channel)

    channels.append(
        Channel(
            channel_id=TEST_ONLY_CHANNEL_ID,
            name="TEST ONLY - Verified Claims",
            source=_TEST_ONLY_SOURCE,
            pillars=_TEST_ONLY_PILLARS,
            verification_policy=test_only_policy or VERIFICATION_REQUIRED,
            active=True,
        )
    )
    return ChannelRegistry(version=1, channels=tuple(channels))


def context_for(registry: ChannelRegistry) -> dict[str, Any]:
    return {CHANNEL_REGISTRY_CONTEXT_KEY: registry}


@pytest.fixture
def test_registry() -> ChannelRegistry:
    return build_registry()


@pytest.fixture
def roblox_record() -> StoryRecord:
    return StoryRecord.model_validate(
        {
            "channel_id": "robloxtales",
            "story_id": "STORY-TEST-1",
            "title": "The door nobody built",
            "premise": "Two friends find a door that was not there yesterday.",
            "classification": "fiction",
            "content_pillar": "mystery",
            "story_mode": "mystery-discovery",
            "emotions": ["curiosity"],
            "verification_status": "not-required",
        }
    )


@pytest.fixture
def legacy_record() -> StoryRecord:
    """A historical record on the retired legacy channel."""

    return StoryRecord.model_validate(
        {
            "channel_id": "legacy-storyteller",
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
