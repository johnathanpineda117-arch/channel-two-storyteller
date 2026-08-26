"""Command-line entry point for validating local story profiles."""

import argparse
import json
from pathlib import Path
from typing import Any, Sequence

from pydantic import ValidationError

from channel2.knowledge import load_catalog
from channel2.models import StoryClassification, StoryRecord
from channel2.pipeline import Pipeline
from channel2.status import capability_rows


EXAMPLE_PROFILE: dict[str, Any] = {
    "story_id": "STORY-001",
    "title": "An unexpected bear encounter",
    "premise": "A man survives an unexpected bear attack.",
    "classification": "nonfiction",
    "content_pillar": "unbelievable-survival",
    "story_mode": "survival",
    "emotions": ["shock", "relief"],
    "verification_status": "unverified",
}


def classification_guidance(record: StoryRecord) -> str:
    if record.classification == StoryClassification.NONFICTION:
        return (
            "PAUSE: This nonfiction story requires reliable sources and human "
            "verification before research can be marked complete."
        )
    if record.classification == StoryClassification.REALITY_INSPIRED:
        return (
            "REVIEW: Keep the story distinct from any specific unverified real "
            "event and label it when viewers could mistake it for fact."
        )
    return (
        "REVIEW: Treat this story as fiction and label it when viewers could "
        "reasonably mistake it for a real event."
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
        record = StoryRecord.model_validate(load_profile(args.input))
    except (OSError, json.JSONDecodeError, ValidationError, ValueError) as error:
        print(f"INVALID STORY PROFILE: {error}")
        return 2

    pipeline = Pipeline(record=record)
    print(record.model_dump_json(indent=2))
    print(f"Knowledge catalog: {catalog.version}")
    print(f"Pipeline stage: {pipeline.stage.value}")
    print(classification_guidance(record))
    print("Publishing: NOT IMPLEMENTED; explicit human approval is mandatory.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
