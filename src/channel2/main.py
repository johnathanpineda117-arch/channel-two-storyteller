"""Command-line entry point for validating local story profiles."""

import argparse
import json
from pathlib import Path
from typing import Any, Sequence

from pydantic import ValidationError

from channel2.knowledge import default_registry, load_catalog
from channel2.models import Channel, StoryRecord
from channel2.pipeline import Pipeline
from channel2.status import capability_rows


EXAMPLE_PROFILE: dict[str, Any] = {
    "channel_id": "robloxtales",
    "story_id": "STORY-001",
    "title": "The friend who took the Robux",
    "premise": "A player lends their savings to a friend who does not give it back.",
    "classification": "fiction",
    "content_pillar": "robux",
    "story_mode": "twist",
    "emotions": ["surprise", "emotion"],
    "verification_status": "not-required",
}


def verification_guidance(record: StoryRecord, channel: Channel) -> str:
    if channel.verification_policy.requires_verification(record.classification):
        return (
            f"PAUSE: Channel '{channel.channel_id}' requires reliable sources "
            f"and human verification for {record.classification.value} stories "
            "before research can be marked complete."
        )
    return (
        f"REVIEW: Channel '{channel.channel_id}' does not require factual "
        f"verification for {record.classification.value} stories. Label the "
        "story when viewers could reasonably mistake it for a real event."
    )


def load_profile(path: Path | None) -> dict[str, Any]:
    if path is None:
        return EXAMPLE_PROFILE.copy()
    return json.loads(path.read_text(encoding="utf-8"))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="channel2",
        description="Validate Channel 2 story records. This CLI cannot publish.",
    )
    parser.add_argument(
        "--input",
        type=Path,
        help="JSON story profile to validate; uses a local example when omitted",
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="print the honest capability ledger instead of a story profile",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.status:
        for capability, status in capability_rows():
            print(f"{status.value:20} {capability}")
        return 0

    try:
        catalog = load_catalog()
    except (OSError, ValueError) as error:
        print(f"KNOWLEDGE CATALOG ERROR: {error}")
        return 1

    try:
        registry = default_registry()
    except (OSError, ValueError) as error:
        print(f"CHANNEL REGISTRY ERROR: {error}")
        return 1

    try:
        record = StoryRecord.model_validate(load_profile(args.input))
    except (OSError, json.JSONDecodeError, ValidationError, ValueError) as error:
        print(f"INVALID STORY PROFILE: {error}")
        return 2

    channel = registry.get(record.channel_id)
    pipeline = Pipeline(record=record, channel=channel)
    print(record.model_dump_json(indent=2))
    print(f"Knowledge catalog: {catalog.version}")
    print(f"Channel: {channel.name} ({channel.channel_id})")
    if not channel.active:
        print(
            "RETIRED CHANNEL: this record stays readable for history, but it "
            "cannot enter production."
        )
    print(f"Pipeline stage: {pipeline.stage.value}")
    print(verification_guidance(record, channel))
    print("Publishing: NOT IMPLEMENTED; explicit human approval is mandatory.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
