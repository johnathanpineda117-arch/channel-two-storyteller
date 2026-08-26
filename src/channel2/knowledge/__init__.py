"""Structured extracts from the Channel 2 design documents."""

from channel2.knowledge.channels import (
    CHANNEL_REGISTRY_CONTEXT_KEY,
    ChannelRegistry,
    UnknownChannelError,
    default_registry,
    load_channels,
    resolve_channel,
)
from channel2.knowledge.loader import KnowledgeCatalog, load_catalog

__all__ = [
    "CHANNEL_REGISTRY_CONTEXT_KEY",
    "ChannelRegistry",
    "KnowledgeCatalog",
    "UnknownChannelError",
    "default_registry",
    "load_catalog",
    "load_channels",
    "resolve_channel",
]
