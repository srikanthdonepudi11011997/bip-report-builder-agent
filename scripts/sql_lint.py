#!/usr/bin/env python3
"""sql_lint.py - convention checks for Oracle BI Publisher data-model SQL.

Implements the machine-checkable rules from knowledge/conventions.md.
It is a heuristic, regex-based linter (not a SQL parser): it is designed to
catch the mistakes that most often break BIP reports, with few false
positives, and to be easy to extend.

Usage:
    python scripts/sql_lint.py path/to/04-data-model.sql --spec path/to/02-spec.json
    python scripts/sql_lint.py file1.sql file2.sql --format json
    python scripts/sql_lint.py --list-rules

Suppress a finding on one line with a trailing comment:
    ... -- lint: disable=BIP010

Exit code: 1 if any ERROR (or any finding with --strict), else 0.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Optional

ERROR = "error"
WARNING = "warning"

# Objects that must not be used, with the reason / alternative.
# Add entries when the debugger learns a new one (conventions C-08).
FORBIDDEN_OBJECTS: dict[str, str] = {
    "PJF_PROJECT_CUSTOMERS": (
        "raises ORA-00942 in some environments; use the PJF_PROJECT_PARTIES chain "
        "filtered on the client-contact role (conventions C-08, lessons L-001)"
    ),
}

RULES: dict[str, tuple[str, str]] = {
    "BIP001": (ERROR, "Multi-select IN (:p) without a COALESCE(:p, NULL) IS NULL guard (C-02)"),
    "BIP002": (WARNING, "*_ID column compared to a string parameter without TO_CHAR() (C-03)"),
    "BIP003": (ERROR, "Date bind used without TRUNC() (C-04)"),
    "BIP004": (ERROR, "_TL table without LANGUAGE = USERENV('LANG') (C-05)"),
    "BIP005": (ERROR, "Forbidden object (C-08)"),
    "BIP006": (WARNING, "SELECT * in a data model (C-09)"),
    "BIP007": (WARNING, "Unresolved {{ENV_PLACEHOLDER}} token (C-10)"),
    "BIP008": (ERROR, "Spec parameter not used in the SQL (C-01)"),
    "BIP009": (WARNING, "Bind variable not declared in the spec (C-01)"),
    "BIP010": (WARNING, "Hard-coded 15-digit Fusion ID without a comment on the same line (C-10)"),
    "BIP011": (ERROR, "Spec column alias missing from the SQL (coverage)"),
}

_SQL_KEYWORDS_AFTER_TABLE = {
    "ON", "WHERE", "JOIN", "LEFT", "RIGHT", "INNER", "OUTER", "FULL", "CROSS",
    "GROUP", "ORDER", "UNION", "MINUS", "INTERSECT", "CONNECT", "START", "USING",
    "HAVING", "NATURAL", "FETCH", "FOR", "PARTITION",
}

_BIND_RE = re.compile(r"(?<![:\w]):([A-Za-z_]\w*)")
_IN_BIND_RE = re.compile(r"\bIN\s*\(\s*:([A-Za-z_]\w*)\s*\)", re.I)
_ID_COMPARE_RE = re.compile(
    r"\b([\w$#]+(?:\.[\w$#]+)?_ID)\s*(?:IN\s*\(\s*:([A-Za-z_]\w*)\s*\)|=\s*:([A-Za-z_]\w*))",
    re.I,
)
_TL_RE = re.compile(r"\b(?:FROM|JOIN)\s+([\w$#]+(?:\.[\w$#]+)?_TL)\b(?:\s+(?:AS\s+)?([A-Za-z_]\w*))?", re.I)
_SELECT_STAR_RE = re.compile(r"\bSELECT\s+(?:DISTINCT\s+)?\*", re.I)
_PLACEHOLDER_RE = re.compile(r"\{\{\s*([A-Za-z0-9_]+)\s*\}\}")
_FUSION_ID_RE = re.compile(r"(?<![\w.])\d{15}(?![\w.])")
_SUPPRESS_RE = re.compile(r"lint:\s*disable=([A-Z0-9_,\s]+)", re.I)


@dataclass
class Finding:
    rule: str
    severity: str
    line: int
    message: str
    file: str = ""

    def format(self) -> str:
        loc = f"{self.file}:{self.line}" if self.file else f"line {self.line}"
        return f"{loc}: {self.severity.upper()} {self.rule} {self.message}"


# ---------------------------------------------------------------------------
# Text preparation
# ---------------------------------------------------------------------------
def mask_sql(sql: str) -> tuple[str, str]:
    """Return (code, code_ns), both the same length as ``sql``.

    code    - comments replaced with spaces (newlines kept), strings intact
    code_ns - additionally, string-literal *contents* replaced with spaces
    """
    code: list[str] = []
    code_ns: list[str] = []
    i, n = 0, len(sql)
    in_str = False

    def blank(text: str) -> str:
        return "".join(ch if ch == "\n" else " " for ch in text)

    while i < n:
        c = sql[i]
        if in_str:
            if c == "'":
                if i + 1 < n and sql[i + 1] == "'":  # escaped quote ''
                    code.append("''")
                    code_ns.append("  ")
                    i += 2
                    continue
                in_str = False
                code.append(c)
                code_ns.append(c)
            else:
                code.append(c)
                code_ns.append("\n" if c == "\n" else " ")
            i += 1
            continue
        if c == "'":
            in_str = True
            code.append(c)
            code_ns.append(c)
            i += 1
            continue
        if sql.startswith("--", i):
            j = sql.find("\n", i)
            j = n if j == -1 else j
            code.append(blank(sql[i:j]))
            code_ns.append(blank(sql[i:j]))
            i = j
            continue
        if sql.startswith("/*", i):
            j = sql.find("*/", i + 2)
            j = n if j == -1 else j + 2
            code.append(blank(sql[i:j]))
            code_ns.append(blank(sql[i:j]))
            i = j
            continue
        code.append(c)
        code_ns.append(c)
        i += 1
    return "".join(code), "".join(code_ns)


def _line_of(text: str, pos: int) -> int:
    return text.count("\n", 0, pos) + 1


def _norm_bind(name: str) -> str:
    return name.lstrip(":").lower()


# ---------------------------------------------------------------------------
# Linting
# ---------------------------------------------------------------------------
def lint_sql(sql: str, spec: Optional[dict] = None, disabled: Iterable[str] = ()) -> list[Finding]:
    """Lint one SQL text. ``spec`` is a parsed 02-spec.json (optional)."""
    disabled_set = {d.strip().upper() for d in disabled if d.strip()}
    code, code_ns = mask_sql(sql)
    findings: list[Finding] = []

    def add(rule: str, line: int, message: str) -> None:
        findings.append(Finding(rule, RULES[rule][0], line, message))

    params = {}
    if spec:
        for p in spec.get("parameters", []) or []:
            if p.get("bind"):
                params[_norm_bind(p["bind"])] = p

    binds_used: dict[str, int] = {}
    for m in _BIND_RE.finditer(code_ns):
        binds_used.setdefault(m.group(1).lower(), _line_of(code_ns, m.start()))

    # BIP001 multi-select guard -------------------------------------------
    reported_001: set[str] = set()
    for m in _IN_BIND_RE.finditer(code_ns):
        bind = m.group(1).lower()
        if bind in reported_001:
            continue
        p = params.get(bind)
        if p is not None and not p.get("multi_select", False):
            continue
        guard = re.compile(rf"COALESCE\s*\(\s*:{re.escape(bind)}\s*,\s*NULL\s*\)\s*IS\s+NULL", re.I)
        if not guard.search(code_ns):
            reported_001.add(bind)
            add("BIP001", _line_of(code_ns, m.start()),
                f"IN (:{bind}) has no 'COALESCE(:{bind}, NULL) IS NULL OR ...' guard")

    # BIP002 TO_CHAR on numeric ID columns ----------------------------------
    for m in _ID_COMPARE_RE.finditer(code_ns):
        col = m.group(1)
        bind = (m.group(2) or m.group(3)).lower()
        is_in_list = m.group(2) is not None
        p = params.get(bind)
        if p is not None:
            fire = p.get("type") == "string" or bool(p.get("compare_to_numeric_column"))
        else:
            fire = is_in_list  # LOV-backed multi-selects pass strings
        if fire:
            add("BIP002", _line_of(code_ns, m.start()),
                f"{col} compared to :{bind} - use TO_CHAR({col}) if the parameter is a string")

    # BIP003 TRUNC on date binds -------------------------------------------
    if params:
        date_binds = {b for b, p in params.items() if p.get("type") == "date"}
    else:
        date_binds = {b for b in binds_used if "date" in b}
    for bind in sorted(date_binds):
        for m in re.finditer(rf"(?<![:\w]):{re.escape(bind)}\b", code_ns, re.I):
            before = code_ns[max(0, m.start() - 40):m.start()]
            after = code_ns[m.end():m.end() + 20]
            if re.search(r"TRUNC\s*\(\s*(?:(?:NVL|COALESCE)\s*\(\s*)?$", before, re.I):
                continue
            if re.match(r"\s*IS\s+(?:NOT\s+)?NULL\b", after, re.I):
                continue
            add("BIP003", _line_of(code_ns, m.start()), f"date bind :{bind} not wrapped in TRUNC()")

    # BIP004 _TL language filter -------------------------------------------
    lang_rhs = r"USERENV\s*\(\s*'LANG'\s*\)"
    for m in _TL_RE.finditer(code_ns):
        table = m.group(1)
        alias = m.group(2)
        if alias and alias.upper() in _SQL_KEYWORDS_AFTER_TABLE:
            alias = None
        if alias:
            qual = re.escape(alias)
        else:
            qual = re.escape(table.split(".")[-1])
        pat = re.compile(
            rf"(?:\b{qual}\s*\.\s*)?LANGUAGE\s*=\s*{lang_rhs}|{lang_rhs}\s*=\s*(?:\b{qual}\s*\.\s*)?LANGUAGE"
            if not alias else
            rf"\b{qual}\s*\.\s*LANGUAGE\s*=\s*{lang_rhs}|{lang_rhs}\s*=\s*\b{qual}\s*\.\s*LANGUAGE",
            re.I,
        )
        if not pat.search(code):
            who = f"{table} {alias}" if alias else table
            add("BIP004", _line_of(code_ns, m.start()),
                f"{who}: add {alias + '.' if alias else ''}language = USERENV('LANG')")

    # BIP005 forbidden objects ---------------------------------------------
    for obj, why in FORBIDDEN_OBJECTS.items():
        for m in re.finditer(rf"\b{re.escape(obj)}\b", code_ns, re.I):
            add("BIP005", _line_of(code_ns, m.start()), f"{obj}: {why}")

    # BIP006 SELECT * -----------------------------------------------------------
    for m in _SELECT_STAR_RE.finditer(code_ns):
        add("BIP006", _line_of(code_ns, m.start()), "list columns explicitly instead of SELECT *")

    # BIP007 unresolved placeholders ---------------------------------------
    seen_tokens: set[str] = set()
    for m in _PLACEHOLDER_RE.finditer(code_ns):
        token = m.group(1)
        if token in seen_tokens:
            continue
        seen_tokens.add(token)
        add("BIP007", _line_of(code_ns, m.start()),
            f"{{{{{token}}}}} is unresolved - set it in private/environment.md")

    # BIP008 / BIP009 spec <-> bind coverage --------------------------------
    if spec is not None:
        for bind, p in params.items():
            if bind not in binds_used:
                add("BIP008", 0, f":{bind} ({p.get('label', bind)}) is declared in the spec but never used")
        for bind, line in binds_used.items():
            if bind not in params:
                add("BIP009", line, f":{bind} is not declared in the spec parameters")

    # BIP010 hard-coded Fusion IDs -----------------------------------------
    orig_lines = sql.split("\n")
    code_lines = code.split("\n")
    ns_lines = code_ns.split("\n")
    for idx, (orig, cl, ns) in enumerate(zip(orig_lines, code_lines, ns_lines), start=1):
        if _FUSION_ID_RE.search(ns):
            # a comment exists on the line if masking comments changed it
            has_comment = orig.rstrip() != cl.rstrip()
            if not has_comment:
                add("BIP010", idx, "15-digit ID literal - add a comment saying what it is "
                                   "(or use an {{ENV}} token)")

    # BIP011 column alias coverage -----------------------------------------
    if spec is not None:
        for col in spec.get("columns", []) or []:
            alias = col.get("alias")
            if alias and not re.search(rf"\bAS\s+\"?{re.escape(alias)}\"?(?![\w$#])", code_ns, re.I):
                add("BIP011", 0, f"column {alias} ({col.get('header', '')}) has no 'AS {alias}' in the SQL")

    # Suppressions and disabled rules -------------------------------------
    result = []
    for f in findings:
        if f.rule in disabled_set:
            continue
        if f.line > 0 and f.line <= len(orig_lines):
            sm = _SUPPRESS_RE.search(orig_lines[f.line - 1])
            if sm and f.rule in {r.strip().upper() for r in sm.group(1).split(",")}:
                continue
        result.append(f)
    result.sort(key=lambda f: (f.line, f.rule))
    return result


def lint_file(path: Path, spec: Optional[dict] = None, disabled: Iterable[str] = ()) -> list[Finding]:
    sql = path.read_text(encoding="utf-8")
    findings = lint_sql(sql, spec=spec, disabled=disabled)
    for f in findings:
        f.file = str(path)
    return findings


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def _build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description="Lint BIP data-model SQL against knowledge/conventions.md")
    ap.add_argument("files", nargs="*", type=Path, help="SQL files to lint")
    ap.add_argument("--spec", type=Path, help="02-spec.json for parameter/column coverage checks")
    ap.add_argument("--format", choices=["text", "json"], default="text")
    ap.add_argument("--disable", default="", help="comma-separated rule IDs to skip, e.g. BIP006,BIP010")
    ap.add_argument("--strict", action="store_true", help="exit 1 on warnings too")
    ap.add_argument("--list-rules", action="store_true", help="print the rule table and exit")
    return ap


def main(argv: Optional[list[str]] = None) -> int:
    args = _build_parser().parse_args(argv)

    if args.list_rules:
        for rule, (sev, desc) in RULES.items():
            print(f"{rule}  {sev:<7}  {desc}")
        return 0
    if not args.files:
        print("error: no SQL files given (see --help)", file=sys.stderr)
        return 2

    spec = None
    if args.spec:
        try:
            spec = json.loads(args.spec.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            print(f"error: cannot read spec {args.spec}: {exc}", file=sys.stderr)
            return 2

    disabled = [d for d in args.disable.split(",") if d.strip()]
    all_findings: list[Finding] = []
    for path in args.files:
        if not path.is_file():
            print(f"error: {path} not found", file=sys.stderr)
            return 2
        all_findings.extend(lint_file(path, spec=spec, disabled=disabled))

    errors = sum(1 for f in all_findings if f.severity == ERROR)
    warnings = sum(1 for f in all_findings if f.severity == WARNING)

    if args.format == "json":
        print(json.dumps({"errors": errors, "warnings": warnings,
                          "findings": [asdict(f) for f in all_findings]}, indent=2))
    else:
        for f in all_findings:
            print(f.format())
        print(f"\n{errors} error(s), {warnings} warning(s)")

    if errors or (args.strict and warnings):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
