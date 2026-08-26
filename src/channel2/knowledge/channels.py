"""Load and validate the packaged channel registry.

Channel configuration is data rather than code so that adding a channel does
not require adding a code branch. Resolution fails closed: an unrecognised
channel raises rather than falling back to any default channel.
"""

from pathlib import Path

import yaml
from pydantic import BaseModel, ConfigDict, Field, model_validator

from channel2.config import load_settings
from channel2.models.channel import Channel


class UnknownChannelError(ValueError):
    """Raised when a channel identifier is not present in the registry."""


class ChannelRegistry(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    version: int = Field(ge=1)
    channels: tuple[Channel, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_identities_are_unique(self) -> "ChannelRegistry":
        for attribute in ("channel_id", "name"):
            values = [getattr(channel, attribute) for channel in self.channels]
            duplicates = sorted({value for value in values if values.count(value) > 1})
            if duplicates:
                raise ValueError(f"duplicate channel {attribute}: {duplicates}")
        return self

    def get(self, channel_id: str) -> Channel:
        for channel in self.channels:
            if channel.channel_id == channel_id:
                return channel
        known = ", ".join(sorted(channel.channel_id for channel in self.channels))
        raise UnknownChannelError(
            f"unknown channel '{channel_id}'; registered channels: {known}"
        )


def load_channels(path: Path | None = None) -> ChannelRegistry:
    """Load the channel registry from the packaged configuration."""

    channels_path = path or load_settings().channels_path
    raw = yaml.safe_load(channels_path.read_text(encoding="utf-8"))
    return ChannelRegistry.model_validate(raw)
