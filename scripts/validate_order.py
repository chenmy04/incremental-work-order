#!/usr/bin/env python3
"""Validate work orders against the incremental-work-order structural contract.

Usage:
  validate_order.py <file-or-dir> [--strict] [--batch <name>] [--json]

Checks (all modes):
  * file name is NNN-slug.md (three digits, kebab-case slug)
  * frontmatter parses; lists are JSON literals; required keys present
  * id/slug agree with the file name; ruling is R-NNNN; write_paths non-empty
  * terminal state list contains a *_DONE entry (and any *_PARTIAL)
  * required sections present, unless waived in the frontmatter `waive` list
  * Requirements: at least one "### Requirement:" and one "#### Scenario:" whose
    body carries **WHEN** and **THEN**
  * Stages: at least one "- [ ]" / "- [x]" checkbox
  * Gates: a markdown table with columns for assertion, counter-example and
    absent-behaviour, and at least one row with non-empty counter-example/absent

--strict adds:
  * Validation section must contain a fenced code block
--batch <name> validates every order declaring that batch in the given directory,
  and additionally requires *every* stage checkbox of *every* order in the batch
  to be ticked (this is the merge gate; mirrors OpenSpec's `validate --archived`).

Exit code 0 = pass, 1 = violations, 2 = usage error.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

NAME_RE = re.compile(r"^(\d{3})-([a-z0-9]+(?:-[a-z0-9]+)*)\.md$")
RULING_RE = re.compile(r"^R-\d{4}$")
REQUIRED_KEYS = ("id", "slug", "batch", "baseline", "ruling", "write_paths", "terminal")
REQUIRED_SECTIONS = (
    "Objective",
    "Current state",
    "Scope",
    "Requirements",
    "Stages",
    "Gates",
    "Validation",
    "DoD",
    "Acceptance",
)


def parse_frontmatter(text: str):
    if not text.startswith("---\n"):
        return None, "missing frontmatter"
    end = text.find("\n---", 4)
    if end < 0:
        return None, "unterminated frontmatter"
    body = text[4:end]
    data = {}
    for line in body.splitlines():
        line = line.rstrip()
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            return None, f"frontmatter line without ':' -> {line[:40]!r}"
        key, _, raw = line.partition(":")
        key, raw = key.strip(), raw.strip()
        try:
            data[key] = json.loads(raw)
        except json.JSONDecodeError:
            data[key] = raw
    return data, None


def section_body(text: str, title: str) -> str | None:
    """Body of a section, ending at the next heading of the same or higher level.

    Sub-headings inside the section (### inside ##) belong to the body - a naive
    "#+" stop condition truncates Requirements at its first "### Requirement:".
    """
    head = re.compile(rf"^(#+)\s*{re.escape(title)}", re.M)
    match = head.search(text)
    if not match:
        return None
    level = len(match.group(1))
    rest = text[match.end():]
    stop = re.compile(rf"^#{{1,{level}}}(?!#)\s", re.M)
    end = stop.search(rest)
    return rest[:end.start()] if end else rest


def validate_one(path: Path, strict: bool):
    problems: list[str] = []
    text = path.read_text(encoding="utf-8")

    name = NAME_RE.match(path.name)
    if not name:
        problems.append("file name must be NNN-slug.md (three digits, kebab-case)")
        number = slug = None
    else:
        number, slug = name.group(1), name.group(2)

    meta, err = parse_frontmatter(text)
    if meta is None:
        problems.append(err or "bad frontmatter")
        meta = {}
    for key in REQUIRED_KEYS:
        if key not in meta:
            problems.append(f"frontmatter missing key: {key}")
    if number and meta.get("id") not in (None, number):
        problems.append(f"frontmatter id {meta.get('id')!r} != file number {number!r}")
    if slug and meta.get("slug") not in (None, slug):
        problems.append(f"frontmatter slug {meta.get('slug')!r} != file slug {slug!r}")
    ruling = meta.get("ruling")
    if not isinstance(ruling, str) or not RULING_RE.match(ruling):
        problems.append(f"ruling must be a quoted R-NNNN id, got {ruling!r} (waiving a ruling is not allowed)")
    paths = meta.get("write_paths")
    if not isinstance(paths, list) or not paths:
        problems.append("write_paths must be a non-empty JSON list")
    terminal = meta.get("terminal")
    if not isinstance(terminal, list) or not terminal:
        problems.append("terminal must be a non-empty JSON list")
    elif not any(isinstance(t, str) and t.endswith("_DONE") for t in terminal):
        problems.append("terminal must contain a *_DONE entry")

    waived = meta.get("waive") if isinstance(meta.get("waive"), list) else []
    waived_keys = set()
    for entry in waived:
        raw_entry = str(entry)
        name, sep, reason = raw_entry.partition(":")
        if not sep or not reason.strip():
            problems.append(f"waive entry {raw_entry!r} must be '<section>: <reason>' with a non-empty reason")
        key = name.strip()
        if key and key not in REQUIRED_SECTIONS:
            problems.append(f"waive entry names an unknown section: {key!r}")
        waived_keys.add(key)
    for title in REQUIRED_SECTIONS:
        if section_body(text, title) is None and title not in waived_keys:
            problems.append(f"missing section: {title} (or waive it with a reason)")

    requirements = section_body(text, "Requirements")
    if requirements is not None:
        if "### Requirement:" not in requirements:
            problems.append("Requirements needs at least one '### Requirement:'")
        for index, block in enumerate(re.split(r"^###\s+Requirement:", requirements, flags=re.M)[1:], 1):
            if "#### Scenario:" not in block:
                problems.append(f"Requirement {index} has no '#### Scenario:' of its own")
        scenarios = re.findall(r"####\s+Scenario:.*?(?=####\s+Scenario:|\Z)", requirements, re.S)
        if not scenarios:
            problems.append("Requirements needs at least one '#### Scenario:'")
        for index, scenario in enumerate(scenarios, 1):
            if "**WHEN**" not in scenario or "**THEN**" not in scenario:
                problems.append(f"scenario {index} must carry both **WHEN** and **THEN**")

    stages = section_body(text, "Stages")
    if stages is not None:
        boxes = re.findall(r"^\s*-\s*\[( |x|X)\]", stages, re.M)
        if not boxes:
            problems.append("Stages needs at least one '- [ ]' or '- [x]' checkbox")

    gates = section_body(text, "Gates")
    if gates is not None:
        rows = [r for r in gates.splitlines() if r.strip().startswith("|")]
        if len(rows) < 3:
            problems.append("Gates needs a table with a header and at least one data row")
        else:
            header, _, *data = rows
            if not re.search(r"反例|counter", header, re.I):
                problems.append("Gates table needs a counter-example column")
            if not re.search(r"缺席|absent", header, re.I):
                problems.append("Gates table needs an absent-behaviour column")
            header_cells = [c.strip() for c in header.strip().strip("|").split("|")]
            if len(header_cells) < 4:
                problems.append("Gates table needs at least four columns: gate / assertion / counter-example / absent")
            for i, raw in enumerate(data, 1):
                if set(raw.strip()) <= set("|-: "):
                    continue  # separator row
                cells = [c.strip() for c in raw.strip().strip("|").split("|")]
                if len(cells) < len(header_cells):
                    problems.append(
                        f"Gates row {i} has {len(cells)} cells but the header declares {len(header_cells)}"
                        " — a short row is a defect, not something to skip"
                    )
                    continue
                if not cells[-2] or not cells[-1]:
                    problems.append(f"Gates row {i} leaves the counter-example or absent cell empty")

    if strict:
        validation = section_body(text, "Validation")
        if validation is not None and "```" not in validation:
            problems.append("strict: Validation needs a fenced code block with runnable commands")

    return problems, meta


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("target", help="order file, directory of orders, or directory of a sub-tree docs/implementation")
    ap.add_argument("--strict", action="store_true")
    ap.add_argument("--batch", metavar="NAME")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    root = Path(args.target)
    if not root.exists():
        print(f"no such path: {root}", file=sys.stderr)
        return 2
    if root.is_dir():
        candidates = sorted((root / "work-orders").glob("*.md")) if (root / "work-orders").is_dir() else sorted(root.glob("*.md"))
    else:
        candidates = [root]
    if not candidates:
        print(f"no order files under {root}", file=sys.stderr)
        return 2

    report = {}
    failed = False
    for path in candidates:
        problems, meta = validate_one(path, args.strict)
        if args.batch:
            if str(meta.get("batch", "")) != args.batch:
                continue
            stages = section_body(path.read_text(encoding="utf-8"), "Stages") or ""
            unticked = len(re.findall(r"^\s*-\s*\[\s\]", stages, re.M))
            if unticked:
                problems.append(f"batch {args.batch}: {unticked} stage checkbox(es) still unticked (merge gate)")
        report[str(path)] = problems
        failed = failed or bool(problems)

    if args.batch and not report:
        print(f"batch {args.batch}: no orders found", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps({"batch": args.batch, "orders": report, "ok": not failed}, ensure_ascii=False, indent=2))
    else:
        for path, problems in report.items():
            if not problems:
                print(f"OK   {path}")
            else:
                print(f"FAIL {path}")
                for problem in problems:
                    print(f"     - {problem}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
