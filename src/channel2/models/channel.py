"""Channel configuration: the isolation boundary for pillars and verification.

A channel owns the subset of :class:`~channel2.models.story.ContentPillar`
terms its records may use, and the policy deciding which story classifications
it publishes and which of those require verified research.

Nothing here is global. A term being defined in the shared vocabulary grants no
channel the right to use it, and a channel that requires verification is
unaffected by another channel that does not.
"""

from pydantic import BaseModel, ConfigDict, Field, model_validator

from channel2.models.story import ContentPillar, StoryClassification


class VerificationPolicy(BaseModel):
    """Channel-scoped replacement for the former global authenticity gate.

    ``verification_required_for`` is the set that used to be hardcoded as
    ``{NONFICTION}`` for every story in the repository. Making it channel data
    keeps the existing research machinery intact while letting a fiction-only
    channel stop being measured against it.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    allowed_classifications: frozenset[StoryClassification] = Field(min_length=1)
    verification_required_for: frozenset[StoryClassification] = frozenset()

    @model_validator(mode="after")
    def validate_required_classifications_are_allowed(self) -> "VerificationPolicy":
        unsupported = self.verification_required_for - self.allowed_classifications
        if unsupported:
            raise ValueError(
                "verification_required_for lists classifications the channel "
                f"does not publish: {sorted(unsupported)}"
            )
        return self

    def allows(self, classification: StoryClassification) -> bool:
        return classification in self.allowed_classifications

    def requires_verification(self, classification: StoryClassification) -> bool:
        return classification in self.verification_required_for


class Channel(BaseModel):
    """A channel's identity, pillar vocabulary, and truth policy.

    ``channel_id`` is the single identity: it is both the stable machine
    identifier records will reference and the registry lookup key. ``name``
    exists only for display and may change without invalidating records.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    channel_id: str = Field(pattern=r"^[a-z0-9]+(-[a-z0-9]+)*$")
    name: str = Field(min_length=1)
    source: str = Field(min_length=1)
    pillars: frozenset[ContentPillar] = Field(min_length=1)
    verification_policy: VerificationPolicy
    active: bool = True

    def allows_pillar(self, pillar: ContentPillar) -> bool:
        return pillar in self.pillars
