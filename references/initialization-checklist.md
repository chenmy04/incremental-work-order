# 初始化清单（空队列、无执行者时）

初始化**只建主树的调度侧那一份**，建完提交并**停下等用户给目标**——不派单、不开树、不起执行者。

## 建这六样

| 文件（默认 `docs/implementation/`，项目已有约定就沿用） | 建的时候装什么 |
| --- | --- |
| `README.md` | 角色 + 索引 + **流程规则**（唯一规则文本）+ 执行者纪律要点；顶部记一行"实例化自 `<skill 名 + 日期>`" |
| `manifest.json` | `orders: []`、`executors: []`、`dispatch_rules`（见下） |
| `status.md` | **汇总账**，首条写**实测基线**：主提交 sha + 跑一次构建/测试的计数与退出码（跑不了就如实写"未跑 + 原因"） |
| `rulings.md` | **裁决账**，编号 `R-0001` 起、只增不改；第一条记"采用本流程" |
| `executor-charter.md` | 执行者纪律（所有执行者共用一份，复制 `assets/executor-charter.md`） |
| `prefs.md` | **偏好账**（复制 `assets/prefs-template.md`；已知偏好填上，其余留默认——`ask` 也是一种偏好） |

```json
{
  "schema_version": 1,
  "scope": "<项目名>",
  "orders": [],
  "executors": [],
  "dispatch_rules": {
    "document": "README.md",
    "approvals": {
      "open_new_worktree_or_executor": "user",
      "merge_back_into_main_worktree": "user",
      "publish_or_scope_widening": "user",
      "loosen_acceptance": "user",
      "dispatch_orders_after_a_confirmed_decision": "scheduler-agent"
    }
  },
  "merge_back": []
}
```

## 条件项：项目计划

**先找**项目已有的计划文档（README / ROADMAP / `docs/**` / issue）：有 → **只记一行指针，不另建、不改它**；
都没有 → 才建最小 `project-plan.md`（目标 / 阶段 / 完成判据 / 明确不做的事）。

## 不建什么

- 任何工作树、执行者、`executors[]` 里的行（**空**——执行者永远在分出去的树上干活）
- 任何工单、`work-orders/` 目录、批次划分（契约落点在子树的 `work-orders/`，派单时才产生）
- 任何"每树一份"的东西（`worktree-charter.md`、执行账、证据目录）
- **不碰 `AGENTS.md`**（项目自己的 agent 指令文件）

## 动作序列

① 侦察（只读）：确认是 git 仓库、落点、**项目已有计划文档在哪**、**实测基线**；
② 建上面六样（+ 条件项）；
③ 在 `rulings.md` 记第一条裁决；
④ 比例化校验（`git diff --check`、`git status --short`）+ **只显式 stage 这几个文件** + 提交；
⑤ 给用户一屏报告：建了什么、实测基线是什么、下一步需要他给什么——并**从实测里主动提 1–2 个候选**给他挑。
