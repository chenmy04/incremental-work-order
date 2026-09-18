"""Per-rule regression tests for scripts/validate_order.py.

Every rule the validator claims gets its own counter-example here: a synthetic order that violates
exactly that rule and must be rejected. A rule without a counter-example is a rule we have not proven.

Run:  python3 -m unittest discover -s tests -v     (or)  python3 tests/test_validate_order.py
No dependencies beyond the standard library.
"""
from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VALIDATOR = ROOT / "scripts" / "validate_order.py"

_spec = importlib.util.spec_from_file_location("validate_order", VALIDATOR)
vo = importlib.util.module_from_spec(_spec)
assert _spec and _spec.loader
_spec.loader.exec_module(vo)

BASE = """---
id: 001
slug: probe
batch: b1
baseline: "aaaa111"
depends_on: []
write_paths: ["src/**"]
forbidden: ["release/**"]
ruling: R-0001
terminal: ["PROBE_DONE", "PROBE_PARTIAL"]
waive: []
---

## Objective
做一件事。

## Current state
`src/x.py:1` 实测如此。

## Scope
| From | To | Reason |
| --- | --- | --- |
| `src/x.py` | `src/y.py` | 归属 |

## Requirements
### Requirement: 新路径可用
#### Scenario: 可以导入
**WHEN** 执行导入
**THEN** 退出码 0

## Stages
- [ ] 1. 记录 baseline（提交）
- [x] 2. 完成迁移（提交）

## Gates
| Gate | Assertion | Counter-example (required) | Absent / unknown ⇒ |
| --- | --- | --- | --- |
| G1 | 引用为 0 | 加回一处导入必须失败 | fail (typed) |

## Validation
```bash
pytest -q
```

## DoD
1..6

## Acceptance
- PROBE_DONE
"""


def check(name: str, text: str, strict: bool = True):
    """Write an order under a matching file name and return its problems."""
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / name
        path.write_text(text, encoding="utf-8")
        problems, _ = vo.validate_one(path, strict)
    return problems


def must_mention(problems, needle: str):
    return any(needle in p for p in problems), problems


class OrderRules(unittest.TestCase):
    def test_baseline_is_accepted(self):
        self.assertEqual(check("001-probe.md", BASE), [])

    # --- filename and identity -------------------------------------------------
    def test_filename_must_be_numbered_and_kebab(self):
        problems = check("probe.md", BASE)
        self.assertTrue(must_mention(problems, "file name must be")[0], problems)

    def test_id_and_slug_must_match_the_filename(self):
        text = BASE.replace("id: 001", "id: 002").replace("slug: probe", "slug: other")
        problems = check("001-probe.md", text)
        self.assertTrue(must_mention(problems, "!=")[0], problems)

    # --- ruling ----------------------------------------------------------------
    def test_ruling_must_be_quoted_id_not_int(self):
        problems = check("001-probe.md", BASE.replace("ruling: R-0001", "ruling: 123"))
        self.assertTrue(must_mention(problems, "quoted R-NNNN")[0], problems)

    def test_ruling_must_follow_the_pattern(self):
        problems = check("001-probe.md", BASE.replace("ruling: R-0001", 'ruling: "R-12"'))
        self.assertTrue(must_mention(problems, "quoted R-NNNN")[0], problems)

    # --- frontmatter lists -----------------------------------------------------
    def test_write_paths_must_be_a_non_empty_list(self):
        problems = check("001-probe.md", BASE.replace('write_paths: ["src/**"]', "write_paths: []"))
        self.assertTrue(must_mention(problems, "write_paths")[0], problems)

    def test_terminal_must_contain_a_done_state(self):
        problems = check("001-probe.md", BASE.replace('terminal: ["PROBE_DONE", "PROBE_PARTIAL"]', 'terminal: ["PROBE_PARTIAL"]'))
        self.assertTrue(must_mention(problems, "*_DONE")[0], problems)

    def test_parallel_units_must_be_a_list_of_strings(self):
        problems = check("001-probe.md", BASE.replace("waive: []", 'waive: []\nparallel_units: ["unit-a", 7]'))
        self.assertTrue(must_mention(problems, "parallel_units")[0], problems)

    def test_parallel_units_must_be_unique(self):
        problems = check("001-probe.md", BASE.replace("waive: []", 'waive: []\nparallel_units: ["unit-a", "unit-a"]'))
        self.assertTrue(must_mention(problems, "must be unique")[0], problems)

    def test_parallel_units_are_optional(self):
        self.assertEqual(check("001-probe.md", BASE.replace("waive: []", 'waive: []\nparallel_units: ["unit-a"]')), [])

    # --- sections and waivers --------------------------------------------------
    def test_missing_section_is_a_problem(self):
        problems = check("001-probe.md", BASE.replace("## Gates\n", "## NotGates\n"))
        self.assertTrue(must_mention(problems, "missing section: Gates")[0], problems)

    def test_waive_entry_must_carry_a_reason(self):
        text = BASE.replace("waive: []", 'waive: ["Gates"]').replace("## Gates\n", "## NotGates\n")
        problems = check("001-probe.md", text)
        self.assertTrue(must_mention(problems, "non-empty reason")[0], problems)

    def test_waive_with_reason_is_accepted(self):
        text = BASE.replace("waive: []", 'waive: ["Gates: 复用主树已有门"]').replace("## Gates\n", "## NotGates\n")
        self.assertEqual(check("001-probe.md", text), [])

    def test_waive_may_not_name_an_unknown_section(self):
        problems = check("001-probe.md", BASE.replace("waive: []", 'waive: ["Gates: x", "Nonsense: y"]'))
        self.assertTrue(must_mention(problems, "unknown section")[0], problems)

    # --- requirements and scenarios -------------------------------------------
    def test_each_requirement_needs_its_own_scenario(self):
        text = BASE.replace(
            "### Requirement: 新路径可用\n#### Scenario: 可以导入\n**WHEN** 执行导入\n**THEN** 退出码 0",
            "### Requirement: 新路径可用\n#### Scenario: 可以导入\n**WHEN** 执行导入\n**THEN** 退出码 0\n\n"
            "### Requirement: 旧路径消失\n**WHEN** 查找旧文件\n**THEN** 不存在",
        )
        problems = check("001-probe.md", text)
        self.assertTrue(must_mention(problems, "has no '#### Scenario:' of its own")[0], problems)

    def test_scenario_needs_when_and_then(self):
        problems = check("001-probe.md", BASE.replace("**THEN** 退出码 0", "结果应当正常"))
        self.assertTrue(must_mention(problems, "must carry both")[0], problems)

    # --- gates -----------------------------------------------------------------
    def test_gate_row_with_empty_counter_or_absent_is_rejected(self):
        problems = check("001-probe.md", BASE.replace("| G1 | 引用为 0 | 加回一处导入必须失败 | fail (typed) |", "| G1 | 引用为 0 | | |"))
        self.assertTrue(must_mention(problems, "leaves the counter-example or absent cell empty")[0], problems)

    def test_short_gate_row_is_a_defect_not_skipped(self):
        problems = check("001-probe.md", BASE.replace("| G1 | 引用为 0 | 加回一处导入必须失败 | fail (typed) |", "| G1 | 引用为 0 |"))
        self.assertTrue(must_mention(problems, "short row is a defect")[0], problems)

    def test_header_must_declare_four_columns(self):
        problems = check("001-probe.md", BASE.replace(
            "| Gate | Assertion | Counter-example (required) | Absent / unknown ⇒ |\n| --- | --- | --- | --- |\n| G1 | 引用为 0 | 加回一处导入必须失败 | fail (typed) |",
            "| Gate | Assertion | Note |\n| --- | --- | --- |\n| G1 | 引用为 0 | n/a |",
        ))
        self.assertTrue(must_mention(problems, "at least four columns")[0], problems)

    # --- strict mode -----------------------------------------------------------
    def test_strict_requires_a_runnable_validation_block(self):
        problems = check("001-probe.md", BASE.replace("```bash\npytest -q\n```", "跑一下测试"))
        self.assertTrue(must_mention(problems, "fenced code block")[0], problems)


class BatchGate(unittest.TestCase):
    """The merge gate: every stage box of every order in the batch must be ticked."""

    def run_batch(self, text: str):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "001-probe.md"
            path.write_text(text, encoding="utf-8")
            return subprocess.run(
                [sys.executable, str(VALIDATOR), str(path), "--batch", "b1", "--strict"],
                capture_output=True, text=True,
            )

    def test_unticked_batch_is_refused(self):
        result = self.run_batch(BASE)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unticked", result.stdout)

    def test_ticked_batch_is_accepted(self):
        result = self.run_batch(BASE.replace("- [ ]", "- [x]"))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
