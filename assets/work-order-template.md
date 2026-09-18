# Work Order <NNN> — <one concrete outcome>

> 契约权威就是这个文件（在**执行树**的 `docs/implementation/work-orders/` 下）。
> 文件名必须是 `NNN-slug.md`；frontmatter 里的列表值是 **JSON**（校验器不依赖 YAML 库）。
> 收口后移到 `work-orders/archive/<YYYY-MM-DD>-NNN-slug.md`（活跃队列保持干净）。
> **投递方式**（调度者）：`git -C <子树> add -N -- <本文件>` 然后
> `git -C <子树> commit -m "dispatch work order <NNN> (from <主树> @<sha>)" -- <本文件>`——
> **绝不要 `git add` 之后裸 `git commit`**（那会把执行者暂存里的东西一起带走，已实测复现）。

```yaml
---
id: 001
slug: move-parser-to-core
batch: b1-parser-move
baseline: "0000000"
depends_on: [{"order": "012", "condition": "merged into main as 0000000"}]
write_paths: ["src/parser/**", "tests/parser/**"]
forbidden: ["release/**"]
ruling: R-0007
terminal: ["PARSER_MOVE_DONE", "PARSER_MOVE_PARTIAL"]
waive: []
parallel_units: []                   # 可选：调度者交底的独立单元；执行者只能在这些单元之间开子代理
---
```

## Objective

<什么会变成真的、为什么现在做、**明确不重做**什么。有人裁决过的引裁决 id 一行。>

## Current state

<带注解的 before/after 树，或一张事实表。每条承重事实带出处：`文件:行`（实测）或"据 报告 日期"（引用）；
未验证的写"未验证/待核实 + 怎么验"。>

```text
before/
├── path/                          ⚠ 实测到的问题
└── stable/                        ✓ 不变

after/
├── destination/                   ◀ 本单改动
└── stable/                        ✓ 不变
```

## Scope

| From | To / action | Reason |
| --- | --- | --- |
| `src/old.py` | `src/new.py` | 归属决定 |

- 必须保持不变的：公开行为 / 标识符 / 签名 / 持久化语义 / 摘要
- 明确**不做**：那些看起来诱人但错的变体，各一句理由
- 不建兼容 shim（除非本单明确授权）

## Requirements

每条需求挂**至少一个**自己的场景——这是执行者在没人可问时的验收依据。

### Requirement: 迁移后可导入

#### Scenario: 新路径可用

**WHEN** 执行 `python -c "import new"`
**THEN** 退出码 0，且 `import old` 抛 ImportError

### Requirement: 旧路径不再存在

#### Scenario: 不留 shim

**WHEN** 查找 `src/old.py`
**THEN** 文件不存在，且全仓无 `old` 的导入

## Stages

每个阶段以**一次阶段性提交**结束，且**用 pathspec 形式提交**：`git commit -m "<msg>" -- <paths>`。
阶段边界 = 重读调度 + 纳入新单/修订 + 留回执的时点。

- [ ] 1. 记录 live baseline 与前置（提交）
- [ ] 2. 第一步机械独立的改动；验证它那段窄接缝（提交）
- [ ] 3. 完成路径/调用方迁移；删掉旧路径，不留 shim（提交）
- [ ] 4. 跑完整验证并把实测数字写进 status（提交）

## Parallel units

<可选，但**写了就等于授权并行**：列出互不相干的单元，每项写"独立于谁、为什么"。执行者只能在这些单元之间
开子代理；没写就单线程做，或说明为什么拆不开。例如：>

- `unit-a`：`src/parser/**` —— 与 `unit-b` 无共享文件、无共同调用方
- `unit-b`：`src/render/**` —— 只读 `unit-a` 的公开接口，接口本单不改

> 子代理**不写契约、不写本树 status、不跑任何 git 写操作**；提交、勾阶段、跑门都由执行者自己做。

## Gates

每道门写清三件事：断言 / **反例（必填）** / **资源缺席或未知时的行为（缺席必须失败）**。
表格四列齐全、**每行填满**——空单元格或少写一个竖线都会被校验器判为缺陷。

| Gate | Assertion | Counter-example (required) | Absent / unknown ⇒ |
| --- | --- | --- | --- |
| G1 导入守卫 | 全仓对旧路径的引用为 0 | 加回一处导入必须让门失败 | fail (typed)，绝不通过 |
| G2 回归套件 | `pytest -q` 退出 0，计数记入 status | 删掉新包必须让它失败 | fail (typed) |

## Validation

```bash
python -c "import new"
pytest -q
python3 scripts/validate_order.py . --strict
git diff --check && git status --short
```

## DoD

1. 实现 · 2. 定向测试**与反例** · 3. 真实环境证据（不是只跑单测） · 4. 回归计数与退出码 ·
5. 账务与清理证据 · 6. status 分账。缺一项 ⇒ 终态写 PARTIAL 并逐条列剩余。

## Acceptance

- 绿：`PARSER_MOVE_DONE`
- 否则：`PARSER_MOVE_PARTIAL` + 精确剩余项与证据

## Notes for the executor

- 需要人拍的事（产品语义/安全/授权/合同）→ 写进本树 `status.md §Questions`（问题 / 选项与代价 / 我的建议），
  **继续做不受影响的其它单**；整队卡死才停。
- 契约有问题 → **不改契约**，交回调度者改并投递新版本；纳入修订后在本树 status 记
  `已纳入 work order <NNN> 修订 @<sha>`。
- **批末**：打 `git tag -a checkpoint/<批次名> -m "<范围> done; suite <计数>; <日期>"`（**tag 不得覆盖**，
  重试用 `-2`），把检查点报告写进本树 status，然后**继续下一批，不为它停下**。
  主树合并时按**这个 tag 指向的 commit sha** 合（`git merge --no-ff <sha>`），**不是**按会继续移动的分支。
- 自检：`python3 <skill>/scripts/validate_order.py . --strict`；
  批次收口/合并前：`--batch <批次名> --strict`（阶段复选框全勾才通过）。

## Checkpoint report（批末写进本树 `status.md` 的格式）

```text
CHECKPOINT <批次名>  [DONE | PARTIAL]   <日期>
1 现在能试什么：逐条给入口/命令 + 期望看到什么
2 要你拍的  ：问题 / 选项与代价 / 我的建议 / 不拍的后果
3 花了什么  ：请求数、估算费用、真实调用次数；清理证据
4 恢复点    ：下一单 + baseline + 有无未提交改动
5 不含糊    ：PARTIAL 不得写成 DONE；门没跑写"未跑"
```
