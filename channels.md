# Channels

A channel is the isolation boundary for identity, content pillars, and
verification policy. Nothing in this repository is allowed to assume a single
global channel definition.

Two rules follow from that:

1. A pillar term existing in the shared vocabulary grants no channel the right
   to use it. A channel may only use the pillars its own configuration lists.
2. Whether a story requires verified research is read from the selected
   channel's policy. There is no global authenticity gate that applies to every
   channel.

The registered channels live in `src/channel2/knowledge/channels.yaml`. This
document defines them; the YAML encodes them. Each pillar term named here is
also an entry in `src/channel2/knowledge/catalog.yaml`, which cites the section
below that defines it.

Other channels in the wider portfolio (MoneyPlayBook, the Bible-focused
channel, Channel 4, and the scenery-view channel) are real and separate, but
their authoritative pillar taxonomies have not been defined here. They are
deliberately not registered rather than encoded from guesswork. Registering one
later is a YAML edit plus a section in this document.

---

## RobloxTales (Block Tales)

RobloxTales / Block Tales is the current Channel 2 direction: short fictional
Roblox stories told for a younger short-form audience.

Stories are invented for entertainment, so the channel publishes `fiction` and
`reality-inspired` work and never presents a story as a documented real event.
Because it makes no factual claims, no classification it publishes requires
verified research. This is a property of the channel's policy, not a weakening
of the verification machinery: a channel whose policy requires verification
still enforces it.

### Friendship

Loyalty, trust, and closeness between characters, including how those bonds are
tested.

### Betrayal

A character breaks trust, changes sides, or exploits a relationship built
earlier in the story.

### Mystery

An unexplained situation inside the fictional world that pulls the viewer
toward an answer. Distinct from the legacy `mystery-strange` pillar, which
covers verified real-world mysteries.

### Fear

Threat, dread, or being hunted, kept at an intensity appropriate for a younger
audience.

### Humor

Comedy arising from character behavior and absurd situations inside the game
world. Distinct from the legacy `funny-relatable` pillar, which is built on
recognizable real-life experience.

### Robux

Stories driven by in-game currency: earning it, losing it, spending it, being
scammed out of it, or being given it unexpectedly.

### Unexpected Twist

The story reverses the meaning of what came before, revealing that the
situation was not what the viewer assumed.

### Survival

Staying alive against a fictional in-game threat. Distinct from the legacy
`unbelievable-survival` pillar, which requires a verified real-world event.

### Social Conflict

Friction between characters or groups: exclusion, rivalry, reputation, status,
and group pressure.

### Perspective Conflict

The same events understood differently by two characters, where the tension
comes from mismatched understanding rather than opposed intent.

---

## Legacy Broad Storyteller

This is the original Channel 2 definition: a broad nonfiction-capable
storytelling channel built on the five pillars in
[content-pillars.md](content-pillars.md), with nonfiction requiring verified
research before production.

It is registered as **inactive**. It is retained so that the old product
knowledge stays readable, so historical records remain interpretable, and so
the previous verification behavior stays reproducible as a regression baseline
rather than being deleted. It must not be used for new content.

Its pillars (`human-stories`, `unbelievable-survival`, `funny-relatable`,
`mystery-strange`, `satisfying-emotional`) keep their original definitions in
[content-pillars.md](content-pillars.md) and are cited from there. They are
deliberately not reused by RobloxTales, because their definitions describe a
different content model: verified real-world events and recognizable real-life
experience rather than invented in-game stories.
