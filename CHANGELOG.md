# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project uses
[Semantic Versioning](https://semver.org/spec/v2.0.0.html) for its skill contract: a breaking change is one that
invalidates an existing order, charter or ledger, or that changes what a conforming order must contain.

## [Unreleased]

## [0.1.0] - 2026-09-18

First public release of the workflow.

### Added

- **The model**: one main tree schedules; each sub-tree executes its own slice of work orders; trees are
  hierarchical (a parent may write the sub-trees it dispatched, inside a whitelist; siblings and outside repos
  get no orders at all).
- **Orders as the contract of record**, living in the executing tree's `docs/implementation/work-orders/`, with
  a fixed structure: JSON frontmatter (id, slug, batch, baseline, decidable dependency conditions, write paths,
  ruling id, terminal codes, waivers), requirements carried as WHEN/THEN scenarios, checkbox stages, and a gates
  table whose counter-example and absent-behaviour columns are mandatory.
- **Batches and checkpoints**: a batch ends with a `checkpoint/<batch>` tag and a checkpoint report in the
  executing tree's own ledger; the executor carries straight on. A checkpoint is an inspection window, not a stop.
- **Delivery is the notification**: writing an order into a sub-tree and committing it there is what notifies the
  executor, which re-reads at every stage boundary; nothing is message-passed between sessions and no copies drift.
- **Ledgers**: a dispatch view (`manifest.json`), a roll-up with known gaps and cost (`status.md`), a citable
  decision ledger (`rulings.md`, `R-0001` …) and a preferences ledger (`prefs.md`).
- **Flexibility with a paper trail**: the rules are defaults; deviations require a written `waive` reason. The
  non-waivable floor is credentials and protected paths, no pushing or auto-merging a mainline, and user approval
  for opening a tree, merging, widening scope or loosening acceptance.
- **Two execution modes**: `dispatch` (sub-tree plus its own long-running session, the default) and `solo` (the
  main tree implements directly, optionally with a subagent, keeping every ledger and gate).
- **`scripts/validate_order.py`** — a dependency-free structural validator: `--strict`, `--json`, and
  `--batch <name>`, whose checkbox check doubles as the merge gate.
- **Anti-false-green checklist**: gates must state what they do when a resource is absent, guards must be proven
  to detect a positive, documentation/code contradictions must not be pinned green by a test, and PARTIAL must
  never be written as DONE.
- **Templates**: work order, worktree charter, preferences ledger, executor capacity ledger, executor charter,
  and the ≤15-line launch prompt that the scheduler hands to the user inline.
- **Eighteen behavioural eval cases** in `evals/evals.json`.

### Notes

- Borrowed with attribution: OpenSpec's strict structural validation and archived-checkbox gate, its
  proposal/tasks layout and its requirement/scenario convention; Spec Kit's per-project constitution, narrowed
  here into a preferences ledger.
- Deliberately not included: session spawning (an agent cannot open a session, so the human pastes the launch
  prompt), dispatching into repositories you do not own, automatic merging, and silent loosening of acceptance.
