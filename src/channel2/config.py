"""Application paths and local configuration."""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    """Filesystem settings with no external-service configuration."""

    repository_root: Path
    knowledge_path: Path
    channels_path: Path
    data_path: Path


def _package_root() -> Path:
    return Path(__file__).resolve().parent


def load_settings(repository_root: Path | None = None) -> Settings:
    """Resolve local project paths without reading environment secrets.

    Packaged resources (the knowledge catalog and channel registry) resolve
    from the installed package. Workspace paths (local data) resolve from the
    repository when running from a source checkout.
    """

    package_root = _package_root()
    root = (repository_root or package_root.parents[1]).resolve()
    return Settings(
        repository_root=root,
        knowledge_path=package_root / "knowledge" / "catalog.yaml",
        channels_path=package_root / "knowledge" / "channels.yaml",
        data_path=root / "data",
    )
