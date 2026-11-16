#!/usr/bin/env python3
"""validate_spec.py - validate a report spec (02-spec.json).

1. JSON Schema validation against templates/fsd-spec.schema.json (needs the
   `jsonschema` package; skipped with a notice if it is not installed).
2. Cross-field checks the schema can't express: unique binds / aliases /
   LOV names / IDs, contiguous column seq, sort and grouping aliases exist.

Usage:
    python scripts/validate_spec.py output/RPT-X/02-spec.json
Exit code: 0 valid, 1 invalid, 2 usage error.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Optional

SCHEMA_PATH = Path(__file__).resolve().parent.parent / "templates" / "fsd-spec.schema.json"


def schema_errors(spec: dict[str, Any], schema_path: Path = SCHEMA_PATH) -> Optional[list[str]]:
    """Return schema errors, or None if jsonschema is not installed."""
    try:
        import jsonschema
    except ImportError:
        return None
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema)
    errors = []
    for err in sorted(validator.iter_errors(spec), key=lambda e: list(e.absolute_path)):
        where = "/".join(str(p) for p in err.absolute_path) or "(root)"
        errors.append(f"schema: {where}: {err.message}")
    return errors


def _dupes(values: list[str]) -> list[str]:
    seen, dupes = set(), []
    for v in values:
        key = v.lower()
        if key in seen and v not in dupes:
            dupes.append(v)
        seen.add(key)
    return dupes


def cross_checks(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    params = spec.get("parameters") or []
    columns = spec.get("columns") or []

    for d in _dupes([p.get("bind", "") for p in params]):
        errors.append(f"duplicate parameter bind {d}")
    # note: one LOV may legitimately serve several parameters, so LOV names are not checked

    aliases = [c.get("alias", "") for c in columns]
    for d in _dupes(aliases):
        errors.append(f"duplicate column alias {d}")
    for a in aliases:
        if len(a) > 30:
            errors.append(f"column alias {a} is longer than 30 characters")

    seqs = sorted(c.get("seq", 0) for c in columns)
    if seqs and seqs != list(range(1, len(seqs) + 1)):
        errors.append(f"column seq values must be 1..{len(seqs)} without gaps, got {seqs}")

    alias_set = {a.upper() for a in aliases}
    for s in spec.get("sorting") or []:
        if s.get("alias", "").upper() not in alias_set:
            errors.append(f"sorting alias {s.get('alias')} is not a column alias")
    for g in spec.get("grouping") or []:
        if g.upper() not in alias_set:
            errors.append(f"grouping alias {g} is not a column alias")

    for key in ("assumptions", "open_questions", "business_rules", "filters"):
        for d in _dupes([i.get("id", "") for i in spec.get(key) or []]):
            errors.append(f"duplicate id {d} in {key}")

    for p in params:
        if p.get("type") == "date" and p.get("multi_select"):
            errors.append(f"{p.get('bind')}: date parameters cannot be multi-select")
    return errors


def validate(spec: dict[str, Any]) -> tuple[list[str], bool]:
    """Return (errors, schema_checked)."""
    s_errors = schema_errors(spec)
    errors = (s_errors or []) + cross_checks(spec)
    return errors, s_errors is not None


def main(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Validate a BIP report spec JSON")
    ap.add_argument("spec", type=Path)
    args = ap.parse_args(argv)
    try:
        spec = json.loads(args.spec.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"error: cannot read {args.spec}: {exc}", file=sys.stderr)
        return 2

    errors, schema_checked = validate(spec)
    if not schema_checked:
        print("note: jsonschema not installed - schema validation skipped (pip install jsonschema)")
    for e in errors:
        print(f"ERROR {e}")
    blocking = [q for q in spec.get("open_questions") or [] if q.get("blocking")]
    print(f"{'INVALID' if errors else 'VALID'}: {len(errors)} error(s); "
          f"{len(spec.get('parameters') or [])} parameters, {len(spec.get('columns') or [])} columns, "
          f"{len(blocking)} blocking open question(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
