"""Configuration tests."""

from pathlib import Path

from channel2 import config as config_module
from channel2.config import load_settings


def test_settings_resolve_package_and_workspace_paths() -> None:
    settings = load_settings()
    package_root = Path(config_module.__file__).resolve().parent

    assert settings.knowledge_path == package_root / "knowledge" / "catalog.yaml"
    assert settings.knowledge_path.is_file()
    assert settings.data_path.is_dir()
