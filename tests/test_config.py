"""Configuration tests."""

from channel2.config import load_settings


def test_settings_resolve_repository_paths() -> None:
    settings = load_settings()

    assert settings.repository_root.name == "channel-two-storyteller" or (
        settings.repository_root.name == "workspace"
    )
    assert settings.knowledge_path.is_file()
    assert settings.data_path.is_dir()
