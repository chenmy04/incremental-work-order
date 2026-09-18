---
id: 001
slug: move-parser-to-core
batch: b1-parser-move
baseline: "8ac89a4"
depends_on: []
write_paths: ["src/parser/**", "src/core/__init__.py", "tests/parser/**"]
forbidden: ["vendor/**", "release/**"]
ruling: R-0003
terminal: ["PARSER_MOVE_DONE", "PARSER_MOVE_PARTIAL"]
waive: []
---

## Objective

Move the parser out of `src/legacy/` into `src/core/parser/` so that `core` no longer imports from `legacy`,
leaving no compatibility shim behind. Deliberately not redesigned here: the parser's own algorithm.

## Current state (measured)

`src/legacy/parser.py` holds the implementation (412 lines, measured `wc -l`); `src/core/__init__.py:7` imports
it; the only other importer is `tests/parser/test_parser.py:3`. `src/legacy/` has one remaining module
(`cli.py`) that stays for now.

```text
before/
├── src/
│   ├── legacy/
│   │   ├── parser.py              ⚠ 412 lines, imported by core/
│   │   └── cli.py                 ✓ stays
│   └── core/
│       └── __init__.py            ⚠ imports legacy.parser
after/
├── src/
│   ├── legacy/
│   │   └── cli.py                 ✓ unchanged
│   └── core/
│       ├── __init__.py            ◀ import updated
│       └── parser/                ◀ moved, 412 lines
└── tests/parser/test_parser.py    ◀ import updated
```

## Scope / Non-goals

| From | To / action | Reason |
| --- | --- | --- |
| `src/legacy/parser.py` | `src/core/parser/__init__.py` | ownership: core owns parsing |
| `src/legacy/cli.py` | unchanged | out of scope |
| `tests/parser/test_parser.py` | import path updated | follow the move |

- Preserve: the public surface `parse(...)`, its exception types and the error message strings.
- Not doing: renaming internal helpers, adding type hints, or introducing a shim module at the old path.
- No new dependencies.

## Requirements

### Requirement: Parsing is reachable from the new path

#### Scenario: Core exposes the parser

**WHEN** a caller runs `python -c "from core import parser; parser.parse('x')"`
**THEN** it succeeds, and `import legacy.parser` raises `ModuleNotFoundError`

### Requirement: The old path is gone, not shimmed

#### Scenario: No compatibility module remains

**WHEN** `src/legacy/parser.py` is looked up after the move
**THEN** the path does not exist and no file in the repository imports `legacy.parser`

## Stages

- [x] 1. Record the live baseline and the importer list (commit)
- [x] 2. Move the file and update the two importers (commit)
- [x] 3. Run the parser suite and the import guard (commit)

## Gates

| Gate | Assertion | Counter-example (required) | Absent / unknown ⇒ |
| --- | --- | --- | --- |
| G1 import guard | `grep -rn "legacy.parser"` returns 0 hits | re-adding one import makes the gate fail | fail (typed), never pass |
| G2 suite | `pytest -q tests/parser` exits 0 with 34 passed | deleting the new package makes it fail | fail (typed) |

## Validation

```bash
python3 -c "from core import parser; parser.parse('x')"
pytest -q tests/parser
python3 scripts/validate_order.py docs/implementation --strict
git diff --check && git status --short
```

## DoD (six pieces)

1. Implementation: move applied, importers updated. 2. Tests and counter-examples: suite green, G1's counter-example
observed failing. 3. Real environment: the module imported from a clean checkout. 4. Regression: 34 passed / 0
failed, exit 0. 5. Accounting and cleanup: no stray copies of the old file, temporary branch removed. 6. Ledger:
this tree's `status.md` updated with the counts.

## Acceptance

- Green: `PARSER_MOVE_DONE`
- Otherwise: `PARSER_MOVE_PARTIAL` with the exact remaining importers and evidence
