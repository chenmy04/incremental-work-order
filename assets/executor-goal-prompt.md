# 执行者启动提示词（≤15 行）

用法：**开新执行者时**由**调度者**填好、**在回复里贴全文**（块前一行写明工作目录），**由用户**粘进新会话。
关键信息都在文档里，所以这段保持这么短。**不要**把它写进某个文件让用户自己去复制。

```text
/goal 你在 <子树绝对路径>（分支 <branch>）里执行派工队列，单内不停。
每阶段边界（= 每次阶段性提交之前）重读：<子树>/docs/implementation/worktree-charter.md，
以及 <主树>/docs/implementation/ 下的 README.md（§3 规则 / §4 纪律）、manifest.json、status.md、rulings.md。
连续跑：批末在自己树上打 git tag -a checkpoint/<批次名>，并把检查点报告写进本树 status，然后继续，不等确认。
需要人拍的部分标成阻塞写进本树 status，继续做不受影响的其它单。
新单与修订由调度者直投进你树的 work-orders/；纳入修订留回执；契约有问题交回调度者。
不合并、不 push、不写 write_paths 之外的东西；只显式 git add -- <paths>。
最终按各单格式给全（门/回归计数/摘要/费用/清理/未做项）与唯一终态码。
```
