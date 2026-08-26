"""CLI and capability-ledger tests."""

import json

from channel2.main import main
from channel2.status import CAPABILITIES, CapabilityStatus


def test_example_profile_is_current_channel_two(capsys) -> None:
    assert main([]) == 0
    output = capsys.readouterr().out

    assert '"story_id": "STORY-001"' in output
    assert '"channel_id": "robloxtales"' in output
    assert "Channel: RobloxTales / Block Tales (robloxtales)" in output
    assert "does not require factual verification" in output
    assert "Publishing: NOT IMPLEMENTED" in output


def test_cli_pauses_a_channel_that_requires_verification(tmp_path, capsys) -> None:
    profile = tmp_path / "legacy.json"
    profile.write_text(
        json.dumps(
            {
                "channel_id": "legacy-storyteller",
                "story_id": "STORY-LEGACY-1",
                "title": "A documented survival event",
                "premise": "A survivor recounts a documented animal encounter.",
                "classification": "nonfiction",
                "content_pillar": "unbelievable-survival",
                "story_mode": "survival",
                "emotions": ["shock"],
                "verification_status": "unverified",
            }
        ),
        encoding="utf-8",
    )

    assert main(["--input", str(profile)]) == 0
    output = capsys.readouterr().out

    assert "PAUSE: Channel 'legacy-storyteller' requires reliable sources" in output
    assert "RETIRED CHANNEL" in output


def test_cli_rejects_a_record_naming_an_unknown_channel(tmp_path, capsys) -> None:
    profile = tmp_path / "unknown.json"
    profile.write_text(
        json.dumps(
            {
                "channel_id": "moneyplaybook",
                "story_id": "STORY-UNKNOWN-1",
                "title": "A story on an unregistered channel",
                "premise": "There is no configuration for this channel.",
                "classification": "fiction",
                "content_pillar": "mystery",
                "story_mode": "twist",
                "emotions": ["surprise"],
                "verification_status": "not-required",
            }
        ),
        encoding="utf-8",
    )

    assert main(["--input", str(profile)]) == 2
    assert "unknown channel 'moneyplaybook'" in capsys.readouterr().out


def test_cli_rejects_invalid_profile(tmp_path, capsys) -> None:
    profile = tmp_path / "invalid.json"
    profile.write_text(json.dumps({"story_id": "bad"}), encoding="utf-8")

    assert main(["--input", str(profile)]) == 2
    assert "INVALID STORY PROFILE" in capsys.readouterr().out


def test_cli_does_not_report_missing_catalog_as_invalid_profile(
    monkeypatch, capsys
) -> None:
    from channel2 import main as main_module

    def missing_catalog():
        raise FileNotFoundError("catalog.yaml")

    monkeypatch.setattr(main_module, "load_catalog", missing_catalog)
    assert main([]) == 1
    output = capsys.readouterr().out
    assert "KNOWLEDGE CATALOG ERROR" in output
    assert "INVALID STORY PROFILE" not in output


def test_status_command_is_explicit(capsys) -> None:
    assert main(["--status"]) == 0
    output = capsys.readouterr().out

    assert "TESTED               story_record_schema" in output
    assert "NOT IMPLEMENTED      autonomous_publishing" in output


def test_tested_capabilities_have_coverage() -> None:
    # This explicit set must be updated with tests before a new capability can
    # truthfully be promoted to TESTED.
    covered = {
        "configuration",
        "story_record_schema",
        "knowledge_catalog",
        "channel_registry",
        "channel_scoped_validation",
        "pipeline_stage_gates",
        "profile_cli",
    }
    declared = {
        name
        for name, status in CAPABILITIES.items()
        if status == CapabilityStatus.TESTED
    }
    assert declared == covered
