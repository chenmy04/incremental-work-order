# incremental-work-order

**A dispatch workflow for long-running coding agents.**
**给长期运行的编码 agent 用的派工流程。**

One main tree schedules; each sub-tree executes its own slice of work orders; batches end in git checkpoints that
are *inspection windows*, not stops; merges back are approval-gated and re-verified on the main tree.

一个主树调度；每棵子树执行自己那一段工单；批次末打的是**检视窗口**而不是停下等审批；合并回主树要你批，
而且**必须在主树重验**。

---

## The problem / 它解决什么

Long-running agent work fails in predictable ways: the plan lives in chat and evaporates; the executor invents
product decisions it had no mandate for; gates go green without proving anything; parallel worktrees fan out and
never merge back; and "done" turns out to be unverified.

长期运行的 agent 作业会以几种可预测的方式坏掉：计划只活在聊天里；执行者替你做产品决策；门绿了却什么都没证明；
并行的工作树只扩不并；"完成了"其实没验过。

This skill is a **repository-backed dispatch process** that fixes those five things. / 这套 skill 是一套
**以仓库为权威**的派工流程，专门修这五件事。

## The model / 模型

```text
user  ⇄  scheduler (main worktree)
          │   plans, writes orders, delivers, observes, merges
          └── authority (repo files)
              ├── README.md       rules + index (single text)
              ├── manifest.json   dispatch view: orders, executors, rules
              ├── status.md       roll-up: states, known gaps, cost
              └── rulings.md      R-0001… citable decisions
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
- **The executor never stops for a checkpoint**. At the end of a batch it tags its tree
  (`checkpoint/<batch>`), writes a checkpoint report into its own status, and carries on. The tag is an
  optional window for you to test what exists.
- **Escalation is not stopping**: a part that needs a human ruling is marked blocked while the executor keeps
  working on everything unaffected.
- **Approval tiers**: the user decides product semantics, security, authorisation, contract changes, opening a
  new tree, merging back, and *loosening* acceptance; the scheduler dispatches, tightens, observes; the executor
  decides only how to implement inside an order.

## Install / 安装

```bash
git clone https://github.com/mmm-05610/incremental-work-order ~/.agents/skills/incremental-work-order
# or, for a single project:  cp -r incremental-work-order <project>/.agents/skills/
```

Works with any agent that can read files and run git; the launch prompt assumes a `/goal`-style long-running
session (ZCode, Claude Code, or any equivalent). A project-local copy shadows a user-level one — keep exactly one.

## Quickstart / 快速开始

1. **Initialise** (no orders yet) — ask your agent:
   > 按 incremental-work-order 初始化这个仓库：建立 `docs/implementation/{README.md, manifest.json, status.md,
   > rulings.md, executor-charter.md}`，orders 与 executors 留空，status 首条写实测基线（提交 sha + 跑一次
   > 构建/测试的计数与退出码）。项目已有计划文档就只记指针。不改业务代码、不碰 AGENTS.md、只显式 stage 并提交。
2. **Dispatch one small thing you already understand** —
   > 我想做 X。按 incremental-work-order 判断能不能派；不能派就告诉我还缺哪个决定。能派就写单、投递、登记。
3. **Open a tree and start an executor** (both need you): approve the tree proposal, then paste the launch
   prompt the scheduler hands you in full into a new session whose working directory is that sub-tree.
4. **Inspect whenever you like** — `git -C <subtree> tag -l 'checkpoint/*'` and read that tree's
   `docs/implementation/status.md` (what to try / what needs your ruling / what was spent / where to resume).
   Try the thing it says works; that is where new problems come from.
5. **Merge at a batch end** — the scheduler proposes, you approve, it merges with `--no-ff`, then **re-runs the
   gates and the full suite on the main tree** instead of trusting the executor's numbers.

## What's inside / 目录

| File | Purpose |
| --- | --- |
| `SKILL.md` | The scheduler's rules — the whole model in one text |
| `GETTING-STARTED.md` | Human onboarding, five steps |
| `assets/work-order-template.md` | The order skeleton (gates with counter-examples and absent-behaviour, DoD six pieces) |
| `assets/worktree-charter-template.md` | The per-tree charter (scope, write rights, slice, batches) |
| `assets/executor-charter.md` | The executor's discipline |
| `assets/executor-goal-prompt.md` | The ≤15-line launch prompt |
| `assets/prefs-template.md` | The preferences ledger (execution mode, approval appetite, cadence, cost cap) |
| `assets/status-template.md` | The executor ledger format, including a questions channel |
| `scripts/validate_order.py` | Structural validator: `--strict`, `--batch <name>` (the merge gate needs every stage box ticked) |
| `references/initialization-checklist.md` | Exactly what to build at init, and what not to |
| `references/false-green-checklist.md` | Seven ways a green gate lies, with three worked cases |
| `evals/evals.json` | Fifteen behavioural test cases (they live here, they are not shipped to consumers) |

## The rules in one screen / 一屏规则

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
11. The scheduler's rules are defaults, not shackles: it consults `prefs.md`, asks once, records the answer, and may
    deviate with a written `waive` reason. The executor side is strict instead - a fixed order format with WHEN/THEN
    scenarios, checkbox stages and a validator - because nobody talks to an executor directly.

## What it deliberately does not do / 明确不做

- No session spawning — an agent cannot open a session; the human pastes the launch prompt. (If your environment
  offers a session-creation entry point and you authorise it, that is your extension.)
- No dispatch to repositories you do not own: bring them into the hierarchy or treat them as read-only.
- No automatic merging, no auto-publish, no silent acceptance loosening.
- No claim that a green suite means anything by itself — see the false-green checklist.

## License

MIT — see [LICENSE](LICENSE).
