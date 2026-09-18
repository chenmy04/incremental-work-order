# incremental-work-order

[English](README.md) · [中文](README.zh-CN.md)

**A dispatch workflow for long-running coding agents.**

One main tree schedules; each sub-tree executes its own slice of work orders; batches end in git checkpoints that
are *inspection windows*, not stops; merges back are approval-gated and re-verified on the main tree.

## The problem

Long-running agent work fails in predictable ways: the plan lives in chat and evaporates; the executor invents
product decisions it had no mandate for; gates go green without proving anything; parallel worktrees fan out and
never merge back; and "done" turns out to be unverified.

This skill is a **repository-backed dispatch process** that fixes those five things.

## The model

```text
user  ⇄  scheduler (main worktree)
          │   plans, writes orders, delivers, observes, merges
          └── authority (repo files)
              ├── README.md       rules + index (single text)
              ├── manifest.json   dispatch view: orders, executors, rules
              ├── status.md       roll-up: states, known gaps, cost
              ├── rulings.md      R-0001… citable decisions
              └── prefs.md        standing user preferences
              └── executor (one long-running session per sub-tree)
                  ├── worktree-charter.md   scope, write rights, slice, batches
                  ├── work-orders/**        the contract of record
                  ├── status.md             execution ledger + checkpoint reports
                  └── evidence/**
```

- **Trees are hierarchical**: a parent may write the sub-trees it dispatched — inside a whitelist
  (`work-orders/**`, `worktree-charter.md`). Sub-trees read the parent, never write it. Siblings never write
  each other. Repos outside the hierarchy are read-only, and **get no orders at all**.
- **Delivery is the notification**: writing an order into the sub-tree and committing it there is what notifies
  the executor — it re-reads its own tree and the main tree's rules/manifest/status at every stage boundary.
  Nothing is message-passed between sessions.
- **The executor never stops for a checkpoint**. At the end of a batch it tags its tree (`checkpoint/<batch>`),
  writes a checkpoint report into its own status, and carries on. The tag is an optional window for you to test
  what already exists.
- **Escalation is not stopping**: a part that needs a human ruling is marked blocked while the executor keeps
  working on everything unaffected.
- **Approval tiers**: the user decides product semantics, security, authorisation, contract changes, opening a
  new tree, merging back, and *loosening* acceptance; the scheduler dispatches, tightens and observes; the
  executor decides only how to implement inside an order.

## Install

```bash
git clone https://github.com/mmm-05610/incremental-work-order ~/.agents/skills/incremental-work-order
# or, for a single project:  cp -r incremental-work-order <project>/.agents/skills/
```

Works with any agent that can read files and run git; the launch prompt assumes a `/goal`-style long-running
session (ZCode, Claude Code, or any equivalent). A project-local copy shadows a user-level one — keep exactly one.

## Quickstart

1. **Initialise** (no orders yet) — ask your agent to run the initialization checklist: build
   `docs/implementation/{README.md, manifest.json, status.md, rulings.md, prefs.md, executor-charter.md}` with
   `orders` and `executors` empty, record a *measured* baseline (commit plus one build/test run with counts and
   exit code), reuse any existing planning document by pointer, and commit with explicit paths. Then it stops and
   asks what you actually want.
2. **Dispatch one small thing you already understand** — the scheduler classifies it, applies the dispatchability
   check, cuts it into ordered work orders, and delivers the first one into a tree.
3. **Open a tree and start an executor** (both need you): approve the tree proposal, then paste the launch prompt
   the scheduler hands you *in full* into a new session whose working directory is that sub-tree.
4. **Inspect whenever you like** — `git -C <subtree> tag -l 'checkpoint/*'` and read that tree's
   `docs/implementation/status.md` (what to try / what needs your ruling / what was spent / where to resume).
   Try the thing it says works; that is where new problems come from.
5. **Merge at a batch end** — the scheduler proposes, you approve, it merges with `--no-ff`, then **re-runs the
   gates and the full suite on the main tree** instead of trusting the executor's numbers.

## What's inside

| File | Purpose |
| --- | --- |
| `SKILL.md` | The scheduler's rules — the whole model in one text |
| `GETTING-STARTED.md` | Human onboarding, five steps |
| `assets/work-order-template.md` | The order skeleton (JSON frontmatter, WHEN/THEN scenarios, checkbox stages, gates with counter-examples and absent-behaviour) |
| `assets/worktree-charter-template.md` | The per-tree charter (scope, write rights, slice, batches) |
| `assets/executor-charter.md` | The executor's discipline |
| `assets/executor-goal-prompt.md` | The ≤15-line launch prompt |
| `assets/prefs-template.md` | The preferences ledger (execution mode, approval appetite, cadence, cost cap) |
| `assets/status-template.md` | The executor ledger format, including a questions channel |
| `scripts/validate_order.py` | Structural validator: `--strict`, `--batch <name>` (the merge gate needs every stage box ticked) |
| `references/initialization-checklist.md` | Exactly what to build at init, and what not to |
| `references/false-green-checklist.md` | Seven ways a green gate lies, with three worked cases |
| `evals/evals.json` | Eighteen behavioural test cases (they live here; they are not shipped to consumers) |
| `examples/` | Conforming, unfinished and non-conforming orders — CI runs all three to prove the gates have teeth |

## The rules in one screen

1. Every order must be executable by someone who only has the repo and cannot read your chat.
2. Facts are graded: measured (with `file:line` or a number), cited (with source and date), or unverified —
   and unverified is never written as measured.
3. Every gate states its counter-example **and** what it does when the resource is absent. Absent means fail.
4. Work is cut by *verifiability and write scope*, not by ambition: one contiguous area → one executor;
   independent areas → one tree each; a shared contract → settle it first, then fan out.
5. Batches belong to the executing tree; the main tree keeps no batch list.
6. Deliver, then let the stage-boundary re-read pick it up. No message passing, no copies, no drift merging.
7. A revision must leave a receipt (`已纳入 work order <N> 修订 @<sha>`) so "did the redirect land" is a fact.
8. PARTIAL is respectable and mergeable — provided the tree is green, the merged part verifiable, and the
   unverified part is recorded as a known gap.
9. Merges are one at a time, re-verified on the main tree, with the approval, conflicts, digests and rollback
   path written down.
10. There is exactly one copy of the rules. Everything else references it.
11. The scheduler's rules are defaults, not shackles: it consults `prefs.md`, asks once, records the answer, and
    may deviate with a written `waive` reason. The executor's side is strict instead — a fixed order format with
    WHEN/THEN scenarios, checkbox stages and a validator — because nobody talks to an executor directly.

## What it deliberately does not do

- No session spawning — an agent cannot open a session; the human pastes the launch prompt. (If your environment
  offers a session-creation entry point and you authorise it, that is your extension.)
- No dispatch to repositories you do not own: bring them into the hierarchy or treat them as read-only.
- No automatic merging, no auto-publish, no silent loosening of acceptance.
- No claim that a green suite means anything by itself — see the false-green checklist.

## Contributing and community

| File | Why it exists |
| --- | --- |
| [CONTRIBUTING.md](CONTRIBUTING.md) | The two invariants (one copy of the rules; every guard must be shown to fail) and how to propose a change |
| [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) | Contributor Covenant v2.1 |
| [SECURITY.md](SECURITY.md) | What counts as a security bug here (an unsafe rule, a gate that cannot fail) and how to report it privately |
| [SUPPORT.md](SUPPORT.md) | Where to ask questions versus where to file bugs |
| [MAINTAINERS.md](MAINTAINERS.md) | Who maintains it and how decisions are made |
| [AGENTS.md](AGENTS.md) | Instructions for agents asked to modify this repo |
| [CHANGELOG.md](CHANGELOG.md) | Keep a Changelog; versions follow the skill contract |
| [CITATION.cff](CITATION.cff) | How to cite this workflow |
| [examples/](examples/) | Conforming, unfinished and non-conforming orders, all exercised by CI |
| [.github/workflows/validate.yml](.github/workflows/validate.yml) | CI: metadata, eval set, validator compiles, conforming passes, unfinished batch blocked, non-conforming rejected |

`python3 scripts/validate_order.py <path> --strict` is the same check CI runs — run it before opening a pull
request.

## License

MIT — see [LICENSE](LICENSE).
