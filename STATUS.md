# Channel 2 Capability Status

This ledger describes executable behavior in the repository. Design documents
describe intent; they do not make a capability implemented.

## TESTED

- Local configuration and project-path resolution
- `StoryRecord` validation and JSON serialization
- Structured knowledge catalog loading
- Controlled vocabulary kept in sync with its documentation, in both directions
- Explicit pipeline stage transitions and terminal human-review state
- CLI validation of story profiles and classification guidance

## IMPLEMENTED

- Python package and local CLI
- Capability registry

## PLANNED

- Research and trend intelligence
- Hook, story, and script generation
- Production planning and storyboarding
- Human draft-review interface
- Manual analytics ingestion and experimentation

## EXPERIMENTAL

- AI video generation
- Trend-mechanism inference
- Automated visual-artifact detection

## FUTURE/CONCEPTUAL

- Continuous multi-platform monitoring
- Semantic audio-visual direction
- Reliable multi-shot character continuity
- Self-tuning creative policy

## NOT IMPLEMENTED

- External API integrations
- Narration and video generation
- Media assembly and quality control
- Publishing preparation
- Autonomous publishing

The automated pipeline has no publishing operation. Its final possible state is
`DRAFT_READY_FOR_HUMAN`, after which a human must review the work.

## Vocabulary provenance

The repository previously carried two parallel schema systems: pydantic models
under `src/channel2/` and JSON Schema files under `specs/` validated by a
hand-written partial draft-07 validator. They used different casing and could
drift silently, and the hand-written validator could not check nested arrays of
objects, so the most detailed part of `experiment_record.schema.json` was never
actually validated. The JSON Schema system was removed and pydantic kept.

Vocabulary carried over into `models/vocabulary.py`: hook types, story
structures, visual formats, tempo, emotional targets, and push/pull decisions.

Vocabulary deliberately **not** carried over, because it belongs to media
assembly, which is not implemented and not planned for the next milestone:
asset types, asset authenticity classification, and generation status. These
remain described in `visual-audio-system.md` and are recoverable from git
history at the commit that removed `specs/`.

Narration perspective was dropped rather than ported: it appeared only in the
deleted JSON schema and is not defined in any design document. It should be
reintroduced with a written definition when a `CreativeProfile` entity exists.

`Tempo` historically existed twice in the deleted JSON schemas, as
`narration_style.speed` and `editing_style.pacing`. The two value sets were
identical (`slow`, `moderate`, `fast`, `variable`), so they were merged into
one enum. The consuming field name will distinguish narration rate from cut
rhythm when those models exist.

## Staged vocabulary

These enums live in `models/vocabulary.py` and the knowledge catalog so they
cannot drift, but they are **not consumed by runtime models** yet:

- `VisualFormat`
- `Tempo`
- `Decision`
- `StoryStructure`

They are staged for a future `CreativeProfile` (and related experiment
records). `StoryStructure` is intentionally not a `StoryRecord` field.

`StoryMode` is a legacy hybrid taxonomy: some values are genre (`survival`,
`emotional`, `funny`) and others are narrative skeletons (`twist`,
`mystery-discovery`, `transformation`, `calm-relief`). It must be decomposed
before `StoryStructure` becomes a first-class experimental variable. This
branch does not invent a replacement taxonomy.

## Known divergence

`README.md` and `content-pillars.md` describe Channel 2 as a broad nonfiction
storytelling channel. The channel is actually RobloxTales / Block Tales, which
publishes fictional Roblox stories to a younger short-form audience and uses a
different pillar taxonomy. The `ContentPillar` enum and the design documents
still reflect the older description.

This is a known, accepted divergence on this branch. The next Channel
milestone will move pillars and verification policy into per-channel
configuration. No real Roblox data should be entered before that milestone
lands; the current required pillar enum cannot represent the actual channel
without misclassification.
