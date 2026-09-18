# Examples

Three sample orders, each proving one thing. CI runs all three; if you change the validator or the order
template, these are the fixtures that must keep behaving.

| Directory | What it proves | Expected |
| --- | --- | --- |
| `conforming/` | A complete, finished order is accepted, and its batch is mergeable | `--strict` **passes**; `--batch <name>` **passes** (every stage box ticked) |
| `incomplete/` | Structure is fine but the work is not finished — the merge gate has teeth | `--strict` **passes**; `--batch <name>` **fails** |
| `nonconforming/` | Defects are caught at all — gates with no counter-example, scenarios without a `**THEN**` | `--strict` **fails** |

Run them yourself:

```bash
python3 scripts/validate_order.py examples/conforming   --strict
python3 scripts/validate_order.py examples/incomplete   --batch b1
python3 scripts/validate_order.py examples/nonconforming --strict; echo "exit=$?"
```
