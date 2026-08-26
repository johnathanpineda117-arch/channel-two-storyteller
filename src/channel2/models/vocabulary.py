"""Controlled vocabulary for creative variables and experiment outcomes.

Every term here is documented in a markdown design file and mirrored in
``knowledge/catalog.yaml``. ``knowledge.loader`` fails if the two drift apart,
so a term cannot exist in code without a written definition behind it.

There is deliberately no ``OTHER`` escape hatch. A creative variable that
cannot be named cannot be compared across videos, which defeats the purpose of
recording it.
"""

from enum import StrEnum


class HookType(StrEnum):
    """Opening technique used to interrupt a scroll."""

    CURIOSITY = "curiosity"
    UNEXPECTED_OUTCOME = "unexpected-outcome"
    QUESTION = "question"
    IMMEDIATE_ACTION = "immediate-action"
    EMOTIONAL = "emotional"
    RELATABLE = "relatable"
    DANGER_SURVIVAL = "danger-survival"
    TRANSFORMATION = "transformation"
    CONTRADICTION = "contradiction"
    QUIET_CURIOSITY = "quiet-curiosity"


class StoryStructure(StrEnum):
    """Narrative skeleton of the story.

    Preserved in the controlled vocabulary and knowledge catalog. Not a
    field on :class:`~channel2.models.story.StoryRecord`:
    :class:`~channel2.models.story.StoryMode` is still a legacy hybrid that
    already encodes some of these sequences, so recording both would make
    experimental attribution impossible. Decompose StoryMode before this
    becomes a first-class experimental variable.
    """

    HOOK_STORY_TWIST = "hook-story-twist"
    HOOK_ESCALATION_PAYOFF = "hook-escalation-payoff"
    QUESTION_INVESTIGATION_ANSWER = "question-investigation-answer"
    SITUATION_CONFLICT_RESOLUTION = "situation-conflict-resolution"
    CURIOSITY_DISCOVERY_REVEAL = "curiosity-discovery-reveal"
    SETUP_EVENT_REACTION = "setup-event-reaction"
    PROBLEM_TRANSFORMATION_SATISFACTION = "problem-transformation-satisfaction"
    CALM_TENSION_RELIEF = "calm-tension-relief"


class VisualFormat(StrEnum):
    """Visual treatment the story is produced in."""

    ROBLOX = "roblox"
    REAL_FOOTAGE = "real-footage"
    CINEMATIC = "cinematic"
    AI_GENERATED = "ai-generated"
    ANIMATION = "animation"
    GAMEPLAY = "gameplay"
    NATURE = "nature"
    ANIMAL = "animal"


class Tempo(StrEnum):
    """Rate shared by narration pacing and visual cut rhythm.

    One enum rather than two identical ones; the field name supplies the
    meaning.
    """

    SLOW = "slow"
    MODERATE = "moderate"
    FAST = "fast"
    VARIABLE = "variable"


class EmotionalTarget(StrEnum):
    """Intended viewer reaction, recorded so it can be compared to the actual
    reaction visible in engagement data."""

    AMUSEMENT = "amusement"
    SHOCK = "shock"
    EMOTION = "emotion"
    CURIOSITY = "curiosity"
    SURPRISE = "surprise"
    RELIEF = "relief"
    GRATITUDE = "gratitude"
    WARMTH = "warmth"
    SATISFACTION = "satisfaction"


class Decision(StrEnum):
    """Outcome of reviewing evidence for a format or experiment.

    ``NO_DECISION`` is the correct answer when evidence is insufficient, and is
    the default rather than a failure state.
    """

    PUSH = "push"
    MAINTAIN = "maintain"
    PULL = "pull"
    REWORK = "rework"
    NO_DECISION = "no-decision"
