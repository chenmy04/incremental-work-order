# Walkthrough — one batch, with a change of plan and a blocker in the middle

A worked case, abridged but faithful: every record quoted below is the record the rules require. It exists to
show what the workflow does when reality interferes — an order appended mid-flight, a decision the executor
cannot make, an answer that arrives as a revision, and a merge that has to be pinned to a snapshot.

Tree in play: `billing/` (branch `feature/refunds`), baseline `0d41c8e`. Main tree: `docs/implementation/`.

## 0. The batch is defined

`billing/docs/implementation/worktree-charter.md` says the slice is orders 001–002, batch `b1-refunds`, and that
the batch ends with `checkpoint/b1-refunds` followed by the checkpoint report. The executor does not stop for it.

## 1. Dispatch

The scheduler writes `work-orders/001-refund-ledger.md` and `002-refund-api.md` directly into the tree and commits
with a pathspec, because the executor shares that index:

```bash
git -C billing add -N -- docs/implementation/work-orders/001-refund-ledger.md
git -C billing commit -m "dispatch work order 001 (from main @a71b2f0)" -- docs/implementation/work-orders/001-refund-ledger.md
```

`manifest.json` now carries, for each order, metadata plus `document: "billing/docs/implementation/work-orders/001-refund-ledger.md@3c9aa1f"`.
Nothing is messaged to the executor; it is mid-order and will read the new files at its next stage boundary.

## 2. The plan changes while the work runs

Mid-batch the user decides partial refunds must be supported too. That is a *decision*, so it is recorded first:

`rulings.md` → `| R-0011 | 2026-09-19 | 支持部分退款；金额以分为单位 | user | order 003 |`

It lands in the **same batch** (queue tail, the running order is not interrupted):

| id | order | batch | depends_on |
| --- | --- | --- | --- |
| 003 | partial refunds | `b1-refunds` | `[{order: "002", condition: "tree commit"}]` |

Delivered the same way. At its next stage boundary the executor sees 003, appends it after 002, and continues.

## 3. The blocker the executor must not decide itself

While implementing 002 the executor hits a product question: *do partial refunds reuse the ledger entry or create
a compensating one?* That is a human ruling. It does **not** stop, and it does **not** invent an answer — it writes
into `billing/docs/implementation/status.md`:

```text
## Blocked
| 单 | 卡在哪 | 类别 | 已做哪些不受影响的部分 |
| 002 | 部分退款复用还是补偿分录 | 产品语义 | 003 的接口骨架与校验已完成，001 已收口 |

## Questions
| 单 | 问题一句话 | 选项与代价 | 我的建议 |
| 002 | 部分退款：复用原分录 vs 补偿分录 | 复用省查询、审计弱；补偿审计强、多一条记录 | 补偿分录 |
```

It carries on with 003. `PARTIAL` is written for 002, not `DONE`.

## 4. The answer arrives as a revision

The user rules: compensating entry. `rulings.md` gets `R-0012`. The scheduler revises order 002 and commits it
again — a new `document@sha`. At the next stage boundary the executor merges the revision into its copy and
records the receipt:

```text
## Receipts
| 单 | 修订 sha | 纳入于 |
| 002 | 8be41c2 | 4d0f9aa (2026-09-19) |
```

`status.md` loses the 002 row from `Blocked`, and 002 proceeds as `DONE`.

## 5. Batch end — a checkpoint, then straight on

```bash
git -C billing tag -a checkpoint/b1-refunds -m "orders 001-003 done; suite 214 passed / 0 failed; 2026-09-19"
```

`status.md` gains the checkpoint report:

```text
CHECKPOINT b1-refunds  [DONE]
1 现在能试什么：POST /refunds 支持全额与部分；入口 `make dev && curl -XPOST localhost:8080/refunds -d '{"amount":1200}'`
2 要你拍的：无
3 花了什么：11 requests, ~$0.04, 0 real-model calls; temp dirs cleaned
4 恢复点：batch b2-statement 从 9f3c1aa 起
```

The tag points at `9f3c1aa`. The executor starts `b2-statement` immediately — the branch moves on.

## 6. Inspection finds something real

The user tries it: a partial refund double-counts the fee. New order `004-refund-fee` is written into `b2-statement`
and delivered. This is the normal path, not an exception: checkpoints exist so that testing happens while work
continues.

## 7. The merge is pinned to the snapshot

The scheduler proposes the merge and names both the tag **and** the sha:

> Merge `billing` at `checkpoint/b1-refunds` = **`9f3c1aa`** — 3 orders, all gates green, suite 214 passed.
> Conflicts expected: none (`docs/` only). Re-verification on the main tree: full suite + digest recompute.
> Rollback: `git revert 9f3c1aa`.

The user approves *that sha*. Two things then matter:

1. **The branch has moved on** (b2 work is in progress), so merging the branch would drag unreviewed work along.
   The command is therefore:

   ```bash
   git -C main rev-parse "checkpoint/b1-refunds^{commit}"   # must print 9f3c1aa, matching merge_back[].sha
   git -C main merge --no-ff 9f3c1aa
   ```

2. **The main tree itself moved** between proposal and merge (another tree landed a commit). The rules say the
   integration conditions are re-checked before merging: the main tree's key gates are re-run, and only then is
   `9f3c1aa` merged.

Afterwards, on the main tree — never the executor's numbers:

```text
suite: 2041 passed / 0 failed (exit 0), digests recomputed
```

`manifest.merge_back[]` records it:

```json
{ "executor": "billing", "approvedBy": "user", "approvedAt": "2026-09-19T09:12:00+08:00",
  "checkpoint": "checkpoint/b1-refunds", "sha": "9f3c1aa", "mergeCommit": "c17b4de",
  "conflicts": [], "reverifiedOnMain": { "suite": "2041 passed / 0 failed", "exit": 0 },
  "rollback": "git revert 9f3c1aa" }
```

The other executor's baseline is updated and it is told; `billing` keeps running `b2-statement` without pausing.

## What this case is meant to show

| Situation | What the rules produced |
| --- | --- |
| A decision arrives mid-batch | A citable ruling, a new order, queue-tail delivery — the running order was not interrupted |
| The executor cannot decide something | It marked the question, kept working on the rest, and stayed `PARTIAL` rather than guessing |
| The answer arrives | A revision with a new sha, and a receipt proving the executor picked it up |
| The batch ends | A tag plus a report usable for testing, and no pause |
| Testing finds a defect | Another ordinary order, not a crisis |
| Approval time | Bound to a commit sha, never to a branch that keeps moving |
| The main tree moved | Integration re-checked before merging, and re-verified after |
