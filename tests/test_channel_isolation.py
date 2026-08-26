"""Behavioral proof that a channel is the isolation boundary.

Every test here goes through ``StoryRecord`` validation or ``Pipeline.advance``.
None of them compare configuration values, because two channels holding
different settings proves nothing about what the code does with them.
"""

from typing import Any

import pytest
from pydantic import ValidationError

from channel2.knowledge import ChannelRegistry, load_channels
from channel2.models import StoryRecord
from channel2.pipeline import Pipeline, PipelineGateError, PipelineStage
from conftest import (
    ROBLOX_VERIFICATION_REQUIRED,
    TEST_ONLY_CHANNEL_ID,
    VERIFICATION_NOT_REQUIRED,
    build_registry,
    context_for,
)


def _payload(**overrides: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "channel_id": "robloxtales",
        "story_id": "STORY-ISO-1",
        "title": "A story used to probe channel boundaries",
        "premise": "The same payload is pointed at different channels.",
        "classification": "fiction",
        "content_pillar": "robux",
        "story_mode": "twist",
        "emotions": ["surprise"],
        "verification_status": "not-required",
    }
    payload.update(overrides)
    return payload


def _validate(payload: dict[str, Any], registry: ChannelRegistry) -> StoryRecord:
    return StoryRecord.model_validate(payload, context=context_for(registry))


def _advance_to_research(record: StoryRecord, registry: ChannelRegistry) -> None:
    pipeline = Pipeline(record=record, channel=registry.get(record.channel_id))
    pipeline.advance(PipelineStage.PROFILE_VALIDATED)
    pipeline.advance(PipelineStage.RESEARCH_COMPLETE)


# --------------------------------------------------------------------------
# Pillar isolation
# --------------------------------------------------------------------------


def test_roblox_pillar_is_accepted_on_roblox() -> None:
    record = _validate(_payload(), build_registry())
    assert record.content_pillar.value == "robux"


def test_legacy_pillar_is_rejected_on_roblox() -> None:
    payload = _payload(content_pillar="unbelievable-survival")

    with pytest.raises(ValidationError, match="does not define the pillar"):
        _validate(payload, build_registry())


def test_roblox_only_pillar_is_rejected_on_another_channel() -> None:
    # Only channel_id differs from the accepted record above.
    payload = _payload(
        channel_id=TEST_ONLY_CHANNEL_ID,
        classification="reality-inspired",
        verification_status="verified",
    )

    with pytest.raises(ValidationError, match="does not define the pillar 'robux'"):
        _validate(payload, build_registry())


def test_a_pillar_shared_by_two_channels_works_on_both() -> None:
    registry = build_registry()

    on_roblox = _validate(_payload(content_pillar="unexpected-twist"), registry)
    on_other = _validate(
        _payload(
            channel_id=TEST_ONLY_CHANNEL_ID,
            content_pillar="unexpected-twist",
            classification="reality-inspired",
            verification_status="verified",
        ),
        registry,
    )

    assert on_roblox.content_pillar == on_other.content_pillar
    assert on_roblox.channel_id != on_other.channel_id


def test_undefined_pillar_is_rejected_everywhere() -> None:
    registry = build_registry()
    for channel_id in ("robloxtales", TEST_ONLY_CHANNEL_ID, "legacy-storyteller"):
        with pytest.raises(ValidationError):
            _validate(_payload(channel_id=channel_id, content_pillar="crypto"), registry)


# --------------------------------------------------------------------------
# Verification isolation
# --------------------------------------------------------------------------


def test_roblox_fiction_passes_the_research_gate() -> None:
    registry = build_registry()
    record = _validate(_payload(), registry)

    _advance_to_research(record, registry)


def test_verification_required_channel_blocks_unverified_content() -> None:
    registry = build_registry()
    record = _validate(
        _payload(
            channel_id=TEST_ONLY_CHANNEL_ID,
            content_pillar="mystery-strange",
            classification="nonfiction",
            verification_status="unverified",
        ),
        registry,
    )

    with pytest.raises(PipelineGateError, match="not sufficiently verified"):
        _advance_to_research(record, registry)


def test_verification_required_channel_accepts_verified_content() -> None:
    registry = build_registry()
    record = _validate(
        _payload(
            channel_id=TEST_ONLY_CHANNEL_ID,
            content_pillar="mystery-strange",
            classification="nonfiction",
            verification_status="verified",
        ),
        registry,
    )

    _advance_to_research(record, registry)


def test_not_required_is_refused_where_verification_is_required() -> None:
    payload = _payload(
        channel_id=TEST_ONLY_CHANNEL_ID,
        content_pillar="mystery-strange",
        classification="nonfiction",
        verification_status="not-required",
    )

    with pytest.raises(ValidationError, match="not an acceptable status"):
        _validate(payload, build_registry())


def test_the_same_payload_is_judged_by_the_channel_it_names() -> None:
    # Identical except for channel_id: permitted by the fiction-friendly
    # channel, refused by the verification-required one.
    registry = build_registry()
    shared = _payload(
        classification="reality-inspired",
        content_pillar="unexpected-twist",
        verification_status="not-required",
    )

    assert _validate(shared, registry).channel_id == "robloxtales"

    with pytest.raises(ValidationError, match="not an acceptable status"):
        _validate({**shared, "channel_id": TEST_ONLY_CHANNEL_ID}, registry)


def test_a_permissive_channel_cannot_launder_verified_only_content() -> None:
    # The mirror case: a verified record is fine on the strict channel and
    # refused on the channel that requires no verification.
    registry = build_registry()
    shared = _payload(
        classification="reality-inspired",
        content_pillar="unexpected-twist",
        verification_status="verified",
    )

    assert _validate(
        {**shared, "channel_id": TEST_ONLY_CHANNEL_ID}, registry
    ).verification_status.value == "verified"

    with pytest.raises(ValidationError, match="does not require verification"):
        _validate(shared, registry)


# --------------------------------------------------------------------------
# Cross-channel independence
# --------------------------------------------------------------------------


def test_changing_roblox_policy_does_not_change_another_channel() -> None:
    strict = _payload(
        channel_id=TEST_ONLY_CHANNEL_ID,
        content_pillar="mystery-strange",
        classification="nonfiction",
        verification_status="unverified",
    )

    for registry in (
        build_registry(),
        build_registry(roblox_policy=ROBLOX_VERIFICATION_REQUIRED),
    ):
        record = _validate(strict, registry)
        with pytest.raises(PipelineGateError, match="not sufficiently verified"):
            _advance_to_research(record, registry)

        verified = _validate({**strict, "verification_status": "verified"}, registry)
        _advance_to_research(verified, registry)


def test_changing_another_channel_policy_does_not_change_roblox() -> None:
    for registry in (
        build_registry(),
        build_registry(test_only_policy=VERIFICATION_NOT_REQUIRED),
    ):
        record = _validate(_payload(), registry)
        _advance_to_research(record, registry)


def test_relaxing_one_channel_does_not_relax_the_other() -> None:
    # Roblox now demands verification while the other channel stops demanding
    # it. Each channel must follow its own new policy, not the other's.
    registry = build_registry(
        roblox_policy=ROBLOX_VERIFICATION_REQUIRED,
        test_only_policy=VERIFICATION_NOT_REQUIRED,
    )

    with pytest.raises(ValidationError, match="not an acceptable status"):
        _validate(_payload(), registry)

    relaxed = _validate(
        _payload(
            channel_id=TEST_ONLY_CHANNEL_ID,
            content_pillar="mystery-strange",
            classification="nonfiction",
            verification_status="not-required",
        ),
        registry,
    )
    _advance_to_research(relaxed, registry)


def test_an_injected_registry_does_not_leak_into_the_default() -> None:
    build_registry(roblox_policy=ROBLOX_VERIFICATION_REQUIRED)

    # The packaged registry is unaffected, so a plain validation still works.
    record = StoryRecord.model_validate(_payload())
    assert record.channel_id == "robloxtales"
    assert TEST_ONLY_CHANNEL_ID not in {
        channel.channel_id for channel in load_channels().channels
    }


def test_a_record_from_an_injected_registry_does_not_survive_without_it() -> None:
    # Re-reading a record resolves its channel again, so a record whose channel
    # only exists in a test registry must fail rather than find a stand-in.
    registry = build_registry()
    record = _validate(
        _payload(
            channel_id=TEST_ONLY_CHANNEL_ID,
            content_pillar="mystery-strange",
            classification="nonfiction",
            verification_status="verified",
        ),
        registry,
    )

    with pytest.raises(ValidationError, match="unknown channel"):
        StoryRecord.model_validate_json(record.model_dump_json())


def test_pipeline_refuses_something_that_is_not_a_record() -> None:
    registry = build_registry()

    with pytest.raises(ValidationError, match="must be a StoryRecord"):
        Pipeline(record={"channel_id": "robloxtales"}, channel=registry.get("robloxtales"))


# --------------------------------------------------------------------------
# Retired channels and unknown channels
# --------------------------------------------------------------------------


def test_historical_record_on_a_retired_channel_still_validates(
    legacy_record: StoryRecord,
) -> None:
    assert legacy_record.channel_id == "legacy-storyteller"
    assert legacy_record.content_pillar.value == "unbelievable-survival"

    restored = StoryRecord.model_validate_json(legacy_record.model_dump_json())
    assert restored == legacy_record


def test_retired_channel_cannot_enter_production(legacy_record: StoryRecord) -> None:
    registry = build_registry()
    pipeline = Pipeline(
        record=legacy_record, channel=registry.get(legacy_record.channel_id)
    )

    with pytest.raises(PipelineGateError, match="is retired"):
        pipeline.advance(PipelineStage.PROFILE_VALIDATED)


def test_unknown_channel_is_rejected_without_falling_back() -> None:
    with pytest.raises(ValidationError, match="unknown channel 'moneyplaybook'"):
        _validate(_payload(channel_id="moneyplaybook"), build_registry())

    with pytest.raises(ValidationError, match="unknown channel"):
        StoryRecord.model_validate(_payload(channel_id="channel-four"))
