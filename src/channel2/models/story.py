"""Core story record for the incremental content pipeline."""

from enum import StrEnum

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    HttpUrl,
    ValidationInfo,
    model_validator,
)

from channel2.models.vocabulary import EmotionalTarget, HookType


class StoryClassification(StrEnum):
    NONFICTION = "nonfiction"
    FICTION = "fiction"
    REALITY_INSPIRED = "reality-inspired"


class ContentPillar(StrEnum):
    """Every pillar term any channel may draw from, not one channel's taxonomy.

    Membership here only means the term has a written definition. Which terms a
    given channel may actually use is decided by that channel's configuration in
    ``knowledge/channels.yaml``; see :mod:`channel2.models.channel`.
    """

    # Legacy broad-storyteller taxonomy, defined in content-pillars.md. Retained
    # so historical records stay interpretable; reachable only from the inactive
    # legacy channel.
    HUMAN_STORIES = "human-stories"
    UNBELIEVABLE_SURVIVAL = "unbelievable-survival"
    FUNNY_RELATABLE = "funny-relatable"
    MYSTERY_STRANGE = "mystery-strange"
    SATISFYING_EMOTIONAL = "satisfying-emotional"

    # RobloxTales / Block Tales, defined in channels.md. Deliberately distinct
    # ids from the legacy terms above: the legacy definitions describe verified
    # real-world events, which is a different content model.
    FRIENDSHIP = "friendship"
    BETRAYAL = "betrayal"
    MYSTERY = "mystery"
    FEAR = "fear"
    HUMOR = "humor"
    ROBUX = "robux"
    UNEXPECTED_TWIST = "unexpected-twist"
    SURVIVAL = "survival"
    SOCIAL_CONFLICT = "social-conflict"
    PERSPECTIVE_CONFLICT = "perspective-conflict"


class StoryMode(StrEnum):
    """Legacy hybrid taxonomy mixing genre and narrative skeleton.

    Several values describe a sequence (twist, mystery-discovery,
    transformation, calm-relief) rather than only an emotional register.
    Decompose this enum before :class:`~channel2.models.vocabulary.StoryStructure`
    becomes a first-class experimental variable. Do not invent a replacement
    taxonomy here.
    """

    TWIST = "twist"
    SURVIVAL = "survival"
    EMOTIONAL = "emotional"
    FUNNY = "funny"
    MYSTERY_DISCOVERY = "mystery-discovery"
    TRANSFORMATION = "transformation"
    CALM_RELIEF = "calm-relief"


class Confidence(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class VerificationStatus(StrEnum):
    NOT_REQUIRED = "not-required"
    UNVERIFIED = "unverified"
    RESEARCHING = "researching"
    PARTIALLY_VERIFIED = "partially-verified"
    VERIFIED = "verified"
    REJECTED = "rejected"


class QcStatus(StrEnum):
    NOT_STARTED = "not-started"
    PASSED = "passed"
    FAILED = "failed"
    FLAGGED_FOR_HUMAN = "flagged-for-human"


class ApprovalStatus(StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CHANGES_REQUESTED = "changes-requested"


class Source(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1)
    url: HttpUrl
    source_type: str = Field(min_length=1)
    notes: str | None = None


class Claim(BaseModel):
    model_config = ConfigDict(extra="forbid")

    text: str = Field(min_length=1)
    verification_status: VerificationStatus = VerificationStatus.UNVERIFIED
    source_urls: list[HttpUrl] = Field(default_factory=list)


class HookOption(BaseModel):
    model_config = ConfigDict(extra="forbid")

    text: str = Field(min_length=1)
    category: HookType
    clickbait_risk: Confidence = Confidence.LOW


class StoryRecord(BaseModel):
    """Versioned shared contract; unfinished fields remain explicitly empty.

    A record carries its channel's stable id, not the channel configuration
    itself, so a channel's pillars or policy can change without rewriting
    history. The rules a record is held to are whichever ones its channel
    defines at validation time.
    """

    model_config = ConfigDict(extra="forbid", use_enum_values=False)

    schema_version: str = "2.0"
    channel_id: str = Field(pattern=r"^[a-z0-9]+(-[a-z0-9]+)*$")
    story_id: str = Field(pattern=r"^STORY-[A-Z0-9][A-Z0-9-]*$")
    title: str = Field(min_length=1)
    premise: str = Field(min_length=1)
    classification: StoryClassification
    content_pillar: ContentPillar
    story_mode: StoryMode
    emotions: list[EmotionalTarget] = Field(min_length=1)

    claims: list[Claim] = Field(default_factory=list)
    sources: list[Source] = Field(default_factory=list)
    verification_status: VerificationStatus
    research_confidence: Confidence = Confidence.LOW

    hook_options: list[HookOption] = Field(default_factory=list)
    selected_hook: HookOption | None = None
    outline: list[str] = Field(default_factory=list)
    script: str | None = None

    asset_ids: list[str] = Field(default_factory=list)
    voice_id: str | None = None
    timeline_path: str | None = None
    draft_path: str | None = None

    qc_status: QcStatus = QcStatus.NOT_STARTED
    approval_status: ApprovalStatus = ApprovalStatus.PENDING
    experiment_ids: list[str] = Field(default_factory=list)
    lessons: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_selected_hook_was_offered(self) -> "StoryRecord":
        if self.selected_hook and self.selected_hook not in self.hook_options:
            raise ValueError("selected_hook must be present in hook_options")
        return self

    @model_validator(mode="after")
    def validate_against_selected_channel(self, info: ValidationInfo) -> "StoryRecord":
        """Hold the record to its own channel's pillars and truth policy.

        A retired channel still validates its historical records; only
        production advancement is blocked, which the pipeline enforces.
        """

        # Deferred: the registry depends on this module's vocabulary, so
        # importing it at module scope would be circular.
        from channel2.knowledge.channels import resolve_channel

        channel = resolve_channel(self.channel_id, info.context)

        if not channel.allows_pillar(self.content_pillar):
            permitted = ", ".join(sorted(pillar.value for pillar in channel.pillars))
            raise ValueError(
                f"channel '{channel.channel_id}' does not define the pillar "
                f"'{self.content_pillar.value}'; it defines {permitted}"
            )

        policy = channel.verification_policy
        if not policy.allows(self.classification):
            published = ", ".join(
                sorted(item.value for item in policy.allowed_classifications)
            )
            raise ValueError(
                f"channel '{channel.channel_id}' does not publish "
                f"'{self.classification.value}' stories; it publishes {published}"
            )

        if policy.requires_verification(self.classification):
            if self.verification_status == VerificationStatus.NOT_REQUIRED:
                raise ValueError(
                    f"channel '{channel.channel_id}' requires verification for "
                    f"'{self.classification.value}' stories, so "
                    f"'not-required' is not an acceptable status"
                )
        elif self.verification_status not in {
            VerificationStatus.NOT_REQUIRED,
            VerificationStatus.REJECTED,
        }:
            raise ValueError(
                f"channel '{channel.channel_id}' does not require verification "
                f"for '{self.classification.value}' stories, so they use "
                f"'not-required' unless they are rejected"
            )
        return self
