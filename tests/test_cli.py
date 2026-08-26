"""CLI and capability-ledger tests."""

import json

from channel2.main import main
from channel2.status import CAPABILITIES, CapabilityStatus


def test_example_cli_pauses_unverified_nonfiction(capsys) -> None:
    assert main([]) == 0
    output = capsys.readouterr().out

    assert '"story_id": "STORY-001"' in output
    assert "PAUSE: This nonfiction story requires" in output
    assert "Publishing: NOT IMPLEMENTED" in output


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
        "pipeline_stage_gates",
        "profile_cli",
    }
    declared = {
        name
        for name, status in CAPABILITIES.items()
        if status == CapabilityStatus.TESTED
    }
    assert declared == covered
