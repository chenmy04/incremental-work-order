# Pull request

## What a reader can now do that they could not before

<!-- One paragraph. "Improves wording" is not an answer; name the action or the decision this unblocks. -->

## What changed

- [ ] Rules: `SKILL.md` only (and nothing else now contradicts it)
- [ ] Behaviour: an eval case added or amended in `evals/evals.json`
- [ ] Order format: `assets/work-order-template.md` **and** `scripts/validate_order.py` updated together
- [ ] Examples: `examples/conforming/` and `examples/nonconforming/` still behave as named
- [ ] Human-facing docs / `CHANGELOG.md` under *Unreleased*

## Checks (paste the output)

```bash
python3 -c "import json,pathlib; json.loads(pathlib.Path('evals/evals.json').read_text())"
python3 -m py_compile scripts/validate_order.py
python3 scripts/validate_order.py examples/conforming --strict            # must pass
python3 scripts/validate_order.py examples/nonconforming --strict; test $? -ne 0   # must fail
```

## House rules

- [ ] One copy of the rules: I did not restate a rule outside `SKILL.md`
- [ ] No private context: no absolute home paths, employer/client names, or unscrubbed real-project examples
- [ ] No new dependencies or vendored code
- [ ] Any new guard has a counter-example proving it rejects something

## Notes for the reviewer

<!-- Anything you were unsure about, plus what you deliberately did not do. -->
