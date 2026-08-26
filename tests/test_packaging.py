"""Smoke-test the built wheel from outside the repository."""

import subprocess
import sys
import zipfile
from pathlib import Path

import pytest

_REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
_VALID_FIXTURE = Path(__file__).resolve().parent / "fixtures" / "valid_story.json"


def test_installed_wheel_cli_from_outside_repo(tmp_path: Path) -> None:
    if sys.version_info < (3, 11):
        pytest.skip("the packaged CLI requires Python 3.11+")
    pytest.importorskip("build")

    dist = tmp_path / "dist"
    venv = tmp_path / "venv"
    work = tmp_path / "outside"
    dist.mkdir()
    work.mkdir()

    build = subprocess.run(
        [
            sys.executable,
            "-m",
            "build",
            "--wheel",
            "--outdir",
            str(dist),
            str(_REPOSITORY_ROOT),
        ],
        capture_output=True,
        text=True,
        check=True,
    )

    wheels = sorted(dist.glob("channel2_content_agent-*.whl"))
    assert wheels, "expected the project wheel in the build output"

    # Packaged data resolves from the installed package, so a resource missing
    # from the wheel only fails once the CLI runs outside a source checkout.
    with zipfile.ZipFile(wheels[-1]) as wheel:
        shipped = set(wheel.namelist())
    for resource in ("catalog.yaml", "channels.yaml"):
        assert f"channel2/knowledge/{resource}" in shipped, (
            f"{resource} is missing from the wheel"
        )

    subprocess.run([sys.executable, "-m", "venv", str(venv)], check=True)
    pip = venv / ("Scripts" if sys.platform == "win32" else "bin") / "pip"
    channel2 = venv / ("Scripts" if sys.platform == "win32" else "bin") / "channel2"
    subprocess.run(
        [str(pip), "install", str(wheels[-1])],
        check=True,
        capture_output=True,
        text=True,
    )

    fixture = work / "valid_story.json"
    fixture.write_text(_VALID_FIXTURE.read_text(encoding="utf-8"), encoding="utf-8")
    result = subprocess.run(
        [str(channel2), "--input", str(fixture)],
        cwd=work,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr + result.stdout
    assert '"story_id": "STORY-FIXTURE-1"' in result.stdout
    assert "INVALID STORY PROFILE" not in result.stdout
    assert "KNOWLEDGE CATALOG ERROR" not in result.stdout
