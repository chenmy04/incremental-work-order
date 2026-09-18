# Work Order <N> — <one concrete outcome>

**Status:** READY_FOR_EXECUTION | BLOCKED (<reason, who must rule>)
**Batch:** <批次名>（批末打 `checkpoint/<批次名>`，然后继续）
**Baseline:** <the commit/checkpoint this order starts from, measured>
**Depends on:** <order ids + which *part* must be landed, as a decidable condition:
`merged into main as <sha>` (default, stronger) or `tree-A commit <sha>` (weaker — say why)>
**Ruling:** <R-0007>（没有裁决来源就别派；需要裁决的先去 `rulings.md` 记一条）

## Objective

<What becomes true, why it matters now, and what is deliberately NOT being redesigned.
If a human ruled something, cite the ruling id in one line.>

## Current state, measured

<Annotated before/after tree, or a table of the exact facts the work depends on. Every load-bearing fact
carries its source: `file:line` (measured) or "per <report>, <date>" (cited). Anything not verified is
written as 未验证/待核实 plus how to verify it.>

```text
before/
├── path/                          ⚠ <measured problem>
└── stable/                        ✓ unchanged

after/
├── destination/                   ◀ changed by work order <N>
└── stable/                        ✓ unchanged
```

## Exact scope

| From | To / action | Reason |
| --- | --- | --- |
| `<path>` | `<path>` | <decided ownership> |

**Write paths:** `<glob>` · **Forbidden write roots:** <other trees, publishing main, protected paths>

## Invariants and non-goals

- Preserve <public behavior / identifiers / signatures / persistence semantics / digests>.
- Do not redesign <adjacent undecided area>.
- Do not create compatibility shims unless explicitly authorized.
- Do not read, modify, or stage <protected paths>.
- Explicitly NOT doing: <the attractive-but-wrong variants, with the one-line reason>.

## Stages and commit boundaries

<The executor's own step/commit rhythm for this order. Each stage ends in a staged commit with explicit paths.>

1. Record the live baseline and prerequisites (commit it).
2. First mechanically independent change; validate its narrow seam (commit it).
3. Finish path/caller migration; remove the old path without a shim (commit it).
4. Run full validation and update status with measured numbers (commit it).

## Gates

Each gate states its assertion, its evidence type, and **what it does when the resource is absent**.

| Gate | Assertion | Counter-example (required) | Absent / unknown ⇒ |
| --- | --- | --- | --- |
| G1 <name> | <what must be observed, with a number> | <the counter-example that must fail> | fail (typed), never pass |
| G2 <name> | ... | ... | ... |

## Validation

```bash
<typecheck>
<targeted tests>
<full relevant tests>
<architecture / collision / digest guard>
git diff --check && git status --short
```

## Checkpoint report (written into this tree's `status.md` at batch end)

```text
CHECKPOINT <批次名>  [DONE | PARTIAL]
1 现在能试什么：逐条给入口/命令 + 期望看到什么
2 要你拍的  ：问题 / 选项与代价 / 我的建议 / 不拍的后果
3 花了什么  ：请求数、估算费用、真实调用次数；清理证据
4 恢复点    ：下一单 + baseline + 有无未提交改动
5 不含糊    ：PARTIAL 不得写成 DONE；门没跑写"未跑"
```

## Stop and report when

- A prerequisite is not satisfied (dependency condition false).
- **A gate cannot pass because a human must rule** (product semantics, security, authorization, contract):
  mark it blocked in this tree's status and **continue with the other orders**; stop entirely only when the
  whole queue is blocked.
- A protected path would need to be touched, or a contract change is needed (**do not edit the contract —
  hand it back to the scheduler**).
- Tests would need semantic assertion changes outside the authorized scope.
- The measured result contradicts this order's baseline or target.

## Definitions of Done (six pieces)

1. Implementation · 2. Targeted tests **and counter-examples** · 3. Real-environment evidence
(not unit tests alone) · 4. Regression counts with exit codes · 5. Accounting and cleanup evidence ·
6. Status ledger updated. Missing any ⇒ the terminal state is PARTIAL, itemised.

## Acceptance state

- Green: `<WORK_ORDER_STATE_GREEN>`
- Otherwise: `<WORK_ORDER_STATE_PARTIAL>` with the exact remaining items and evidence.
