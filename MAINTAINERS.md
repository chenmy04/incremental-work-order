# Maintainers

## Current

| Maintainer | Scope |
| --- | --- |
| [@mmm-05610](https://github.com/mmm-05610) | Everything: triage, review, releases, security reports |

## What a maintainer does here

1. **Guards the two invariants** from [CONTRIBUTING.md](CONTRIBUTING.md): exactly one copy of the rules, and no
   guard without a counter-example that proves it rejects something.
2. **Reviews against the model, not taste**: does the change create a second source of truth, make an
   unenforceable rule, or let an agent widen its own scope? Those are the only reasons to reject outright.
3. **Keeps CI honest**: `examples/` must keep proving the gates in both directions; a change that makes the
   non-conforming example pass is reverted or the example is replaced with a better one — never weakened.
4. **Releases**: anything a consumer would notice goes under *Unreleased* in [CHANGELOG.md](CHANGELOG.md), and a
   breaking change (one that invalidates an existing order, charter or ledger, or that changes what a conforming
   order must contain) bumps the minor version while the contract is pre-1.0.
5. **Handles security reports privately** per [SECURITY.md](SECURITY.md) and notes the outcome in the changelog
   once a fix ships.

## Repository protections

`main` and the release tags are guarded by repository rulesets; both have an **empty bypass list**, so the
maintainer is bound by them too.

| Ruleset | Applies to | Enforced |
| --- | --- | --- |
| `protect-main` | the default branch | pull request required (0 approvals while there is one maintainer, all review threads resolved), the `validate` check required and the branch must be up to date, force-pushes and deletions refused |
| `protect-release-tags` | tags matching `refs/tags/v*` | deleting or moving a published tag is refused (creating a new tag is allowed) |

Consequences worth knowing: **changes land through a pull request**, so a commit that skips CI is impossible even
for the maintainer; the escape hatch for an outage is editing the ruleset itself, which is visible in the audit
log rather than a standing bypass. When a second maintainer joins, raise the approval count to one and turn on
code-owner review — until then, one approval would deadlock the only maintainer, since GitHub does not let you
approve your own pull request.

## How decisions are made

- Small fixes — wording, a missing counter-example, a typo — land by pull request at the maintainer's discretion.
- Model changes (a new object, a new phase, a relaxation or a new hard rule) start as an issue, get a stated
  recommendation, and are left open for comment before merging. If there is no objection that survives one round
  of replies, the maintainer merges and records the reasoning in the pull request.
- Anything that changes the safety floor in [SKILL.md](SKILL.md) (credentials, protected paths, no pushing or
  auto-merging a mainline, user approval for opening a tree / merging / widening scope / loosening acceptance)
  requires an explicit note in the changelog explaining why the floor is still sound.
- Decisions that reverse an earlier one are recorded, not silently rewritten: the old rule stays visible in the
  changelog so adopters can see what changed and when.

## Becoming a maintainer

Sustained, good-faith contributions — several merged pull requests that respect the invariants, plus issue triage
in an area you know — earn an invitation. There is no formal process beyond that; ask.

## 中文要点

- 维护者的职责是**守两条不变量**（规则只有一份；每道门都要被证明能拒绝东西），不是审文风。
- 模型变更先开 issue、给建议、留一轮评论再合；**安全地板**（凭据、受保护路径、不推送/不自动合并、
  开树/合并/扩权/放宽验收要用户批）的任何改动都必须在 changelog 里写清理由。
- 变更决定要**记录反转**，不静默改写历史；持续贡献 + 参与 triage 会收到邀请。
