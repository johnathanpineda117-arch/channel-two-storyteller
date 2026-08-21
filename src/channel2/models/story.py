"""Core story record for the incremental content pipeline."""

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, model_validator


class StoryClassification(StrEnum):
    NONFICTION = "nonfiction"
    FICTION = "fiction"
    REALITY_INSPIRED = "reality-inspired"


class ContentPillar(StrEnum):
    HUMAN_STORIES = "human-stories"
    UNBELIEVABLE_SURVIVAL = "unbelievable-survival"
    FUNNY_RELATABLE = "funny-relatable"
    MYSTERY_STRANGE = "mystery-strange"
    SATISFYING_EMOTIONAL = "satisfying-emotional"


class StoryMode(StrEnum):
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
    category: str = Field(min_length=1)
    clickbait_risk: Confidence = Confidence.LOW


class StoryRecord(BaseModel):
    """Versioned shared contract; unfinished fields remain explicitly empty."""

    model_config = ConfigDict(extra="forbid", use_enum_values=False)

    schema_version: str = "1.0"
    story_id: str = Field(pattern=r"^STORY-[A-Z0-9][A-Z0-9-]*$")
    title: str = Field(min_length=1)
    premise: str = Field(min_length=1)
    classification: StoryClassification
    content_pillar: ContentPillar
    story_mode: StoryMode
    emotions: list[str] = Field(min_length=1)

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
    def validate_classification_rules(self) -> "StoryRecord":
        if (
            self.classification == StoryClassification.NONFICTION
            and self.verification_status == VerificationStatus.NOT_REQUIRED
        ):
            raise ValueError("nonfiction cannot use verification status 'not-required'")
        if (
            self.classification != StoryClassification.NONFICTION
            and self.verification_status
            not in {VerificationStatus.NOT_REQUIRED, VerificationStatus.REJECTED}
        ):
            raise ValueError(
                "fiction and reality-inspired stories use 'not-required' "
                "unless they are rejected"
            )
        if self.selected_hook and self.selected_hook not in self.hook_options:
            raise ValueError("selected_hook must be present in hook_options")
        return self
