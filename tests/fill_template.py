"""Run the shipped work-order template through the validator, the way a user would.

Used by CI as an anti-rot gate: the template a user copies must satisfy the validator a user runs.

Sequence (all must hold):
  1. fill the template's placeholders -> a conforming order -> `--strict` passes
  2. its batch is NOT mergeable while the stage boxes are unticked -> `--batch NAME` fails
  3. tick the boxes -> `--batch NAME` passes

Exit code 0 when every step behaves as above, 1 otherwise.
"""
from __future__ import annotations

import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "assets" / "work-order-template.md"
VALIDATOR = ROOT / "scripts" / "validate_order.py"


def instantiate(template: str) -> str:
    """Replace <placeholder> angle-bracket tokens with concrete values.

    Only tokens that survive inside code blocks and tables are replaced; the YAML frontmatter is
    rebuilt explicitly so the JSON lists stay valid.
    """
    body = template
    # frontmatter: replace the whole illustrative block with a concrete one
    body = re.sub(
        r"```yaml\n---\n.*?\n---\n```",
        """```yaml
---
id: 001
slug: template-fixture
batch: b1-template-fixture
baseline: "0000000"
depends_on: []
write_paths: ["src/**"]
forbidden: ["release/**"]
ruling: R-0001
terminal: ["FIXTURE_DONE", "FIXTURE_PARTIAL"]
waive: []
parallelism: "none"
parallelism_reason: "template fixture"
---
```""",
        body,
        flags=re.S,
    )
    # the fence marker before the frontmatter makes the file start with prose; strip the leading note
    body = body.split("```yaml", 1)[1]
    body = "---" + body.split("---", 1)[1]
    # table cells and bullets: replace remaining <...> tokens
    body = re.sub(r"<[^<>\n]{1,60}>", "placeholder", body)
    return body


def run(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(VALIDATOR), *args], capture_output=True, text=True)


def main() -> int:
    if not TEMPLATE.is_file():
        print(f"missing template: {TEMPLATE}")
        return 1
    with tempfile.TemporaryDirectory() as tmp:
        order = Path(tmp) / "001-template-fixture.md"
        text = instantiate(TEMPLATE.read_text(encoding="utf-8"))
        text = text.replace("- [ ]", "- [ ]")  # keep unticked for step 2
        order.write_text(text, encoding="utf-8")

        strict = run([str(order), "--strict"])
        if strict.returncode != 0:
            print("FAIL: a filled-in shipped template does not pass --strict")
            print(strict.stdout or strict.stderr)
            return 1
        print("ok: filled template passes --strict")

        batch = run([str(order), "--batch", "b1-template-fixture", "--strict"])
        if batch.returncode == 0:
            print("FAIL: an unfinished batch was reported mergeable")
            return 1
        print("ok: unfinished batch is refused")

        finished = order.read_text(encoding="utf-8").replace("- [ ]", "- [x]")
        order.write_text(finished, encoding="utf-8")
        batch_done = run([str(order), "--batch", "b1-template-fixture", "--strict"])
        if batch_done.returncode != 0:
            print("FAIL: a finished batch is still refused")
            print(batch_done.stdout or batch_done.stderr)
            return 1
        print("ok: finished batch passes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
