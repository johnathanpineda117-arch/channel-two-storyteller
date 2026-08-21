"""Application paths and local configuration."""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    """Filesystem settings with no external-service configuration."""

    repository_root: Path
    knowledge_path: Path
    data_path: Path


def load_settings(repository_root: Path | None = None) -> Settings:
    """Resolve local project paths without reading environment secrets."""

    root = (repository_root or Path(__file__).resolve().parents[2]).resolve()
    return Settings(
        repository_root=root,
        knowledge_path=root / "src" / "channel2" / "knowledge" / "catalog.yaml",
        data_path=root / "data",
    )
