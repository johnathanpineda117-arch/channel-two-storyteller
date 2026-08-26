# Channel 2 — Storyteller

> **Current direction:** Channel 2 is **RobloxTales / Block Tales**, publishing
> fictional Roblox stories. Sections 1–13 below describe the original broad
> nonfiction storytelling direction, which is **legacy** and is registered as
> the retired `legacy-storyteller` channel. They are kept because they remain
> the authoritative definition of the legacy vocabulary that historical records
> use. See [channels.md](channels.md) for current channel configuration and
> [STATUS.md](STATUS.md) for what is actually implemented.

## 1. Mission

Build a scalable YouTube Shorts entertainment channel centered around short-form storytelling, memorable visual experiences, humor, curiosity, emotion, and satisfying payoffs.

The channel is designed to become part of a larger passive-content portfolio while maintaining originality, quality, authenticity, and audience trust.

The goal is not to copy existing channels.

The goal is to identify what makes short-form storytelling entertaining, test those principles through original content, measure the results, and systematically improve.

---

## 2. Viewer Experience

The viewer should feel:

- Curious
- Entertained
- Surprised
- Emotionally engaged
- Satisfied
- Relieved
- Occasionally grateful or humbled

Primary emotional reactions:

- 😂 Funny
- 🤯 Unexpected
- ❤️ Emotional
- 👀 Curious

Target viewer journey:

STOP → CURIOSITY → ENGAGEMENT → EMOTIONAL REACTION → PAYOFF → SATISFACTION

---

## 3. Content Philosophy

Channel 2 will use a broad entertainment storytelling model rather than being restricted to a single subject.

Potential content areas include:

- Human behavior
- Relationships and dating
- Friendship
- Family
- History
- Strange facts
- Animals
- Dark stories
- Funny stories
- Satisfying transformations
- Unexpected events
- Survival stories
- "You won't believe what happened" stories

Content may include:

- Nonfiction stories
- Clearly labeled fictional stories
- Stories inspired by real-world situations

Nonfiction claims must be researched and verified before being presented as factual.

Fiction must never be intentionally presented as a real event.

---

## 4. Visual Philosophy

Visuals should be attention-grabbing while still feeling intentional and authentic.

Potential visual approaches include:

- Vibrant visuals
- Cinematic visuals
- Authentic real-world footage
- AI-generated visuals when appropriate
- Satisfying transformations
- Nature and environmental imagery
- Story-specific visual sequences

AI-generated media should not be used simply because it is available.

The visual choice should serve the story.

The channel should avoid creating an obvious low-quality or generic AI-generated appearance.

---

## 5. Retention Philosophy

Videos may use:

- Rapid cuts
- Strategic zooms
- Sound effects
- Word-by-word captions
- Frequent visual changes
- Music progression
- Audio transitions
- Curiosity gaps
- Story escalation
- Unexpected reveals
- Satisfying payoffs

However, stimulation should not become overwhelming.

The goal is high engagement without making the viewer feel overstimulated.

---

## 6. Storytelling

Stories may use different structures depending on the subject.

Possible structures include:

- Hook → Story → Twist
- Hook → Escalation → Payoff
- Question → Investigation → Answer
- Situation → Conflict → Resolution
- Curiosity → Discovery → Reveal
- Setup → Unexpected Event → Reaction
- Calm → Tension → Relief
- Problem → Transformation → Satisfaction

The ending may be:

- Unexpected
- Funny
- Emotional
- Satisfying
- Peaceful
- Relieving
- Informative

---

## 7. Voice & Audio

The channel may use different narration styles and voices depending on the story.

Audio should support the emotional direction of the video.

Potential elements:

- Narration
- Music
- Sound effects
- Environmental audio
- Silence or reduced audio for emphasis

The channel should avoid repetitive narration that makes every video feel mechanically generated.

---

## 8. Quality Standards

Videos should NOT feel:

- Boring
- Overstimulating
- Obviously AI-generated
- Excessively dark
- Cringey
- Aggressively promotional
- Confusing
- Emotionally empty

Every video should pass a quality review before publication.

---

## 9. Analytics & Experimentation

Channel 2 will use an experiment-driven approach.

Process:

IDEA → TEST → PUBLISH → MEASURE → REVIEW → PUSH / PULL → ITERATE

A single video should not automatically determine whether an idea succeeds or fails.

Variables may be tested independently, including:

- Hook
- Story type
- Video length
- Pacing
- Visual style
- Caption style
- Narration
- Audio
- Emotional payoff
- Ending
- Subject matter

Successful patterns should receive additional testing and production.

Underperforming patterns should be modified, retested, or discontinued based on evidence.

---

## 10. Community & Engagement

The goal is to create videos that naturally encourage viewers to relate their own experiences to the story.

Desired reactions include:

- "That's so funny 😂"
- "Me and my friend had something like that happen 😂"
- "That somehow brought back a memory 😂"

Comments should feel natural rather than artificially requested.

Creator comments may be tested as an engagement variable and evaluated through analytics.

---

## 11. Production Philosophy

Initial production should prioritize legitimate free or low-cost tools and sources.

Sources and tools should be reviewed for:

- Authenticity
- Legitimacy
- Usage rights
- Reliability
- Quality
- Suitability for the intended video

The production system should prioritize original or properly licensed/usable material.

---

## 12. Automation Vision

The long-term system may support:

IDEA
→ RESEARCH
→ VERIFICATION
→ SCRIPT
→ VOICE
→ VISUALS
→ EDIT
→ QUALITY CONTROL
→ PUBLISH
→ ANALYTICS
→ LEARNING
→ NEXT TEST

Automation should assist production rather than remove human judgment.

The system should eventually identify successful patterns and use those findings to improve future content.

---

## 13. Portfolio Philosophy

Channel 2 is being developed as an experiment-driven content asset within a larger YouTube portfolio.

The objective is not to maximize output blindly.

The objective is to discover repeatable formats that produce strong viewer response and then scale the formats supported by evidence.

Quality → Testing → Data → Learning → Scale

---

## 14. Phase 1 Foundation

The repository now includes a local, testable Python foundation. It validates
structured story records, enforces ordered pipeline stage gates, and holds the
project's controlled vocabulary in a single place: the enums in
`src/channel2/models/vocabulary.py` must match `knowledge/catalog.yaml` entry
for entry, and each catalog entry cites the design-document section that
defines it. A term cannot enter the code without a written definition.

Run the tests with Python 3.11 or newer. The suite reads the source tree
directly, so no install step is required:

```bash
python -m pytest
```

To use the CLI, install the package first:

```bash
python -m pip install -e ".[dev]"
python -m channel2.main
python -m channel2.main --status
```

Validate a local JSON story profile with:

```bash
python -m channel2.main --input path/to/story.json
```

This phase does not research, generate scripts or media, run media quality
control, integrate external APIs, or publish. The automated state machine ends
at `DRAFT_READY_FOR_HUMAN`; it deliberately has no publishing operation. See
[STATUS.md](STATUS.md) for the capability ledger.

## 15. Channel Isolation

The channel is the isolation boundary. Every story record names its channel:

```json
{ "channel_id": "robloxtales", "content_pillar": "robux", "...": "..." }
```

A record is validated against the pillars and verification policy of the
channel it names, and nothing else. A pillar belonging to another channel is
rejected, a classification the channel does not publish is rejected, and a
verification status inconsistent with the channel's policy is rejected. An
unrecognised channel is rejected rather than defaulted.

Retired channels (`active: false`) keep working for history: their records
still load and validate against their own taxonomy and policy. What they cannot
do is enter production, which the pipeline enforces.

Channels are documented in [channels.md](channels.md) and encoded in
`src/channel2/knowledge/channels.yaml`.