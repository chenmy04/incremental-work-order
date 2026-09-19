# <子树名> 工作树章程

> 由**调度者**写、**执行者**读。规则正文**引用**主树的 `docs/implementation/README.md`，**不要复制**。
> 复制路径：`<子树>/docs/implementation/worktree-charter.md`

## 1 我是谁

- 工作树：`<绝对路径>`　分支：`<branch>`　基线：`<commit sha>`
- 我做什么：<一句话范围>
- 我**不**做什么：<邻接边界；例如"不是 X；不继承 Y 的队列；不碰 Z" >

## 2 写权

- **可写**：`<代码/配置路径清单>`、`docs/implementation/work-orders/**`（契约权威）、
  `docs/implementation/status.md`（我的执行账）、`evidence/**`
- **禁止写**：主树的任何文件、别的子树、发布源、受保护路径：`<清单>`
- 只显式 `git add -- <paths>`；不 `reset`/`stash`/`clean`、不 `merge` 主干、**不 push**

## 3 队列切片（我按这个顺序干）

| 顺序 | 单 | 一句话 | 依赖条件 |
| --- | --- | --- | --- |
| 1 | `<N1>` | <目标> | <已满足 / `merged into main as <sha>`> |
| 2 | `<N2>` | <目标> | 依赖 `<N1>` |

> 新单由调度者直接投递进 `docs/implementation/work-orders/`；我**每个阶段边界**重读该目录并纳入。

## 3b 并行预算（执行者侧）

- 允许开子代理并行：<是/否>；**同时在跑 ≤ <N，默认 4；由调度者与用户商议后写进 prefs>**；**深度 ≤1**（子代理不再开子代理）
- 只允许在**工单声明的 `parallel_units`** 之间并行；工单写 `parallelism: "none"` 就单线程——
  **缺声明是调度者的漏项**（校验器会点名），执行者遇到就交回，不要自己猜
- 子代理**不执行 git 写操作**、不写契约、不写本树 `status.md`；提交、勾阶段、跑门都由执行者本人完成
- 子代理的请求数与费用计入本树 `§Spend`，受 `prefs.md` 的成本上限约束
- 项目 `AGENTS.md` 的模型/数量限额与本节叠加，**取更严者**

## 4 批次与检查点

- **批次 <批次名>**：`<N1, N2, N3>` 做完 → 我打 `git tag -a checkpoint/<批次名> -m "<范围> done; suite <计数>; <日期>"`
  + 把检查点报告写进本树 `status.md` → **然后立刻继续下一批，不为它停下**。
- 批次由调度者与用户商定，只写在这里（主树不存批次清单）。
- tag 唯一、**禁止 `-f` 覆盖**；重试用 `<批次名>-2`。
- **合并按 tag 指向的 commit sha**（`git merge --no-ff <sha>`），不是按会继续移动的分支——我不为检查点停下，
  所以主树批准的对象必须是我打的那个快照。

## 5 每个阶段边界重读什么（只读，不复制）

```bash
cat <本树>/docs/implementation/worktree-charter.md      # 本文件：范围/写权/切片/批次
ls  <本树>/docs/implementation/work-orders/             # 我的契约与新增单（契约权威在这里）
cat <主树>/docs/implementation/README.md                # §3 流程规则 + §4 执行者纪律
cat <主树>/docs/implementation/manifest.json            # 队列 / 依赖条件 / executors
cat <主树>/docs/implementation/status.md                # 进展与阻塞
cat <主树>/docs/implementation/rulings.md               # 裁决账（单里引的 R-xxxx）
```

- **阶段边界 = 每次阶段性提交之前**。
- 纳入**修订**要留回执：下一个阶段提交信息或本树 `status.md` 里记 `已纳入 work order <N> 修订 @<sha>`。
- 契约有问题 → 不改契约，交回调度者。

## 6 证据与账

- 证据落点：`evidence/<order>/`（门报告、日志、摘要；**凭据绝不落盘**）。
- 我的账是本树 `docs/implementation/status.md`：初始化基线、每单阶段与计数、检查点报告、阻塞与剩余项。

## 7 纪律

见主树 `docs/implementation/executor-charter.md`（单内不停、升级标阻塞继续做别的、事实分级、反假绿、凭据）。
