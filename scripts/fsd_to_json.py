#!/usr/bin/env python3
"""fsd_to_json.py - extract text and tables from a Functional Spec (FSD).

Supports .docx (python-docx), .pdf (pdfplumber) and .md/.txt (no deps).
The output is *raw* structure (sections + tables + a few hints). Turning it
into the structured spec (02-spec.json) is the fsd-parser sub-agent's job.

Usage:
    python scripts/fsd_to_json.py inputs/My_FSD.docx -o output/RPT-X/01-fsd-raw.json
    python scripts/fsd_to_json.py examples/sample-ppm-task-listing/fsd-input.md
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Optional

Block = dict[str, Any]

SUPPORTED = {".docx", ".pdf", ".md", ".markdown", ".txt"}

_HINT_KEYS = {
    "report_id": {"reportid", "reportno", "reportnumber", "reportcode"},
    "title": {"reportname", "reporttitle", "title"},
    "module": {"module", "application", "pillar"},
}


# ---------------------------------------------------------------------------
# Extractors -> ordered list of blocks:
#   {"type": "heading", "level": int, "text": str}
#   {"type": "paragraph", "text": str}
#   {"type": "table", "rows": [[str, ...], ...]}
# ---------------------------------------------------------------------------
def _clean(text: Optional[str]) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def extract_docx(path: Path) -> list[Block]:
    try:
        import docx  # python-docx
        from docx.table import Table
        from docx.text.paragraph import Paragraph
    except ImportError as exc:  # pragma: no cover - environment dependent
        raise RuntimeError("python-docx is required for .docx files: pip install python-docx") from exc

    document = docx.Document(str(path))
    blocks: list[Block] = []
    for child in document.element.body.iterchildren():
        tag = child.tag.rsplit("}", 1)[-1]
        if tag == "p":
            para = Paragraph(child, document)
            text = _clean(para.text)
            if not text:
                continue
            style = (para.style.name if para.style is not None else "") or ""
            m = re.match(r"Heading\s*(\d+)", style, re.I)
            if m:
                blocks.append({"type": "heading", "level": int(m.group(1)), "text": text})
            elif style.lower() == "title":
                blocks.append({"type": "heading", "level": 1, "text": text})
            else:
                blocks.append({"type": "paragraph", "text": text})
        elif tag == "tbl":
            table = Table(child, document)
            rows = []
            for row in table.rows:
                # horizontally merged cells are returned once per grid column but
                # share the same underlying <w:tc>; keep each physical cell once
                cells: list[str] = []
                prev_tc = None
                for cell in row.cells:
                    if prev_tc is not None and cell._tc is prev_tc:
                        continue
                    prev_tc = cell._tc
                    cells.append(_clean(cell.text))
                rows.append(cells)
            if rows:
                blocks.append({"type": "table", "rows": rows})
    return blocks


_PDF_HEADING_RE = re.compile(r"^(\d+(?:\.\d+)*)\.?\s+([A-Z][^.]{1,80})$")


def extract_pdf(path: Path) -> list[Block]:
    try:
        import pdfplumber
    except ImportError as exc:  # pragma: no cover - environment dependent
        raise RuntimeError("pdfplumber is required for .pdf files: pip install pdfplumber") from exc

    blocks: list[Block] = []
    with pdfplumber.open(str(path)) as pdf:
        for page in pdf.pages:
            for line in (page.extract_text() or "").splitlines():
                text = _clean(line)
                if not text:
                    continue
                m = _PDF_HEADING_RE.match(text)
                if m:
                    blocks.append({"type": "heading", "level": m.group(1).count(".") + 1, "text": text})
                else:
                    blocks.append({"type": "paragraph", "text": text})
            for table in page.extract_tables() or []:
                rows = [[_clean(c) for c in row] for row in table if row]
                if rows:
                    blocks.append({"type": "table", "rows": rows})
    return blocks


_MD_SEP_CELL = re.compile(r"^:?-{3,}:?$")


def _md_cells(line: str) -> list[str]:
    return [_clean(c) for c in line.strip().strip("|").split("|")]


def extract_markdown(text: str) -> list[Block]:
    blocks: list[Block] = []
    table: list[list[str]] = []

    def flush_table() -> None:
        if table:
            blocks.append({"type": "table", "rows": list(table)})
            table.clear()

    for raw in text.splitlines():
        line = raw.strip()
        if line.startswith("|"):
            cells = _md_cells(line)
            if cells and all(_MD_SEP_CELL.match(c) for c in cells if c) and any(cells):
                continue  # |---|---| separator row
            table.append(cells)
            continue
        flush_table()
        if not line:
            continue
        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        if m:
            blocks.append({"type": "heading", "level": len(m.group(1)), "text": _clean(m.group(2))})
        else:
            blocks.append({"type": "paragraph", "text": _clean(line.lstrip(">").strip())})
    flush_table()
    return blocks


# ---------------------------------------------------------------------------
# Structuring
# ---------------------------------------------------------------------------
def _norm_key(text: str) -> str:
    return re.sub(r"[^a-z0-9]", "", text.lower())


def build_document(blocks: list[Block], source_name: str, fmt: str) -> dict[str, Any]:
    sections: list[dict[str, Any]] = []
    tables: list[dict[str, Any]] = []
    current: dict[str, Any] = {"heading": "", "level": 0, "text": [], "tables": []}

    for block in blocks:
        if block["type"] == "heading":
            if current["heading"] or current["text"] or current["tables"]:
                sections.append(current)
            current = {"heading": block["text"], "level": block["level"], "text": [], "tables": []}
        elif block["type"] == "paragraph":
            current["text"].append(block["text"])
        elif block["type"] == "table":
            rows = block["rows"]
            idx = len(tables)
            tables.append({
                "index": idx,
                "section": current["heading"],
                "header": rows[0],
                "rows": rows[1:],
            })
            current["tables"].append(idx)
    if current["heading"] or current["text"] or current["tables"]:
        sections.append(current)

    for s in sections:
        s["text"] = "\n".join(s["text"])

    return {
        "source": source_name,
        "format": fmt,
        "sections": sections,
        "tables": tables,
        "hints": derive_hints(sections, tables),
    }


def derive_hints(sections: list[dict[str, Any]], tables: list[dict[str, Any]]) -> dict[str, Any]:
    hints: dict[str, Any] = {"report_id": None, "title": None, "module": None,
                             "parameter_tables": [], "column_tables": []}

    # key/value lookups in tables (header row included: some FSDs have no header)
    for t in tables:
        for row in [t["header"], *t["rows"]]:
            if len(row) < 2:
                continue
            key = _norm_key(row[0])
            value = row[1].strip()
            for hint, keys in _HINT_KEYS.items():
                if hints[hint] is None and key in keys and value:
                    hints[hint] = value

    # free-text fallback for the report ID
    if hints["report_id"] is None:
        all_text = "\n".join(s["text"] for s in sections)
        m = re.search(r"Report\s*(?:ID|No\.?|Number)\s*[:#-]?\s*([A-Za-z0-9_.-]+)", all_text, re.I)
        if m:
            hints["report_id"] = m.group(1)

    # classify tables
    for t in tables:
        header = " ".join(t["header"]).lower()
        if "parameter" in header or "prompt" in header:
            hints["parameter_tables"].append(t["index"])
        elif "column" in header or "field" in header:
            hints["column_tables"].append(t["index"])
    return hints


def convert(path: Path) -> dict[str, Any]:
    suffix = path.suffix.lower()
    if suffix not in SUPPORTED:
        raise ValueError(f"unsupported file type '{suffix}' (supported: {', '.join(sorted(SUPPORTED))})")
    if suffix == ".docx":
        blocks, fmt = extract_docx(path), "docx"
    elif suffix == ".pdf":
        blocks, fmt = extract_pdf(path), "pdf"
    else:
        blocks, fmt = extract_markdown(path.read_text(encoding="utf-8")), "markdown"
    # only the file name, never the full local path (privacy)
    return build_document(blocks, path.name, fmt)


def main(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Extract text and tables from an FSD into JSON")
    ap.add_argument("fsd", type=Path, help="FSD file (.docx, .pdf, .md, .txt)")
    ap.add_argument("-o", "--output", type=Path, help="output JSON path (default: stdout)")
    args = ap.parse_args(argv)

    if not args.fsd.is_file():
        print(f"error: {args.fsd} not found", file=sys.stderr)
        return 2
    try:
        doc = convert(args.fsd)
    except (ValueError, RuntimeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    payload = json.dumps(doc, indent=2, ensure_ascii=False)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload + "\n", encoding="utf-8")
        h = doc["hints"]
        print(f"wrote {args.output}: {len(doc['sections'])} sections, {len(doc['tables'])} tables, "
              f"report_id={h['report_id']!r}, parameter_tables={h['parameter_tables']}, "
              f"column_tables={h['column_tables']}")
    else:
        print(payload)
    return 0


if __name__ == "__main__":
    sys.exit(main())
