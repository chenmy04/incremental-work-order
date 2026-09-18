# Contributing

Thanks for wanting to improve this workflow. It is a small repo: mostly Markdown plus one dependency-free
Python script, so contributions are cheap to review — provided they respect the two rules that make the whole
thing work.

## The two rules

1. **There is exactly one copy of the rules.** `SKILL.md` is the only place the workflow's rules live.
   `GETTING-STARTED.md`, the assets and the references may *point* at it; they must not restate it.
   If you find the same rule written twice, that is a bug — send the fix.
2. **Every rule must be checkable, and every guard must be proven to fail.** A gate that has never been
   shown to reject anything is not a gate. `scripts/validate_order.py` is the executable part of this repo:
   `examples/conforming/` must pass and `examples/nonconforming/` must fail, and CI enforces both directions.

## How to propose a change

1. Open an issue first for anything that changes the model (a new object, a new phase, a relaxation of a
   rule). Small fixes — typos, clearer wording, a missing counter-example — can go straight to a pull request.
2. Keep the change *proportional*: a wording fix needs no eval; a behaviour change needs a new eval case in
   `evals/evals.json` and, if it touches the order format, an update to `assets/work-order-template.md`
   **and** the validator.
3. Run the same checks CI runs, locally:

```bash
python3 -c "import json,pathlib; json.loads(pathlib.Path('evals/evals.json').read_text())"
python3 -m py_compile scripts/validate_order.py
python3 scripts/validate_order.py examples/conforming --strict          # must pass
python3 scripts/validate_order.py examples/nonconforming --strict; test $? -ne 0   # must fail
```

4. Write the pull request against `.github/PULL_REQUEST_TEMPLATE.md`. State what a reader can now do that
   they could not before, and which check proves it.

## What we do not accept

- **Private context**: absolute home paths, employer names, client names, or examples lifted from a real
  project without scrubbing. This repo is public and generic.
- **Unenforceable advice**: "make sure to test properly" is not a rule this workflow can carry. Rewrite it as
  something a validator, a counter-example, or a fixed document section can check.
- **Duplicated rules** (see rule 1) or process for its own sake. If a step does not change what someone does,
  delete it.
- **Vendored code or dependencies**: the validator must stay runnable with a stock Python 3 and no installs.

## Commit style

One intent per commit, imperative subject, body explaining *why* if the change is not obvious. If a commit's
message and its tree disagree, fix the tree with a follow-up commit rather than rewriting published history.

## Translations

`README.md` is English and `README.zh-CN.md` is Chinese; change one and update the other in the same pull
request. Further languages are welcome as `README.<lang>.md`, linked from the switcher line at the top of
`README.md`. Keep `SKILL.md` in the language the maintainer reviews best — translate the human-facing entry
points, not the rules.

## 中文要点

- 两条底线：**规则只有一份**（只写在 `SKILL.md`，别处只引用）；**每道门都必须被证明能拒绝东西**
  （`examples/conforming` 必须过、`examples/nonconforming` 必须挂，CI 双向校验）。
- 改行为 → 加一条 eval；改工单格式 → 同时改模板与校验器。提 PR 前在本地跑一遍 CI 的四条命令。
- 不接受：私有路径/真实项目名、无法校验的空话、重复的规则、引入依赖。
