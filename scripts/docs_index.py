#!/usr/bin/env python3
"""docs_index.py - local, dependency-light RAG index over your configuration docs.

Drop configuration workbooks / setup documents (DFF definitions, value sets,
lookups, custom roles, BU/ledger setup, design docs ...) into the docs library
folder, then:

    python scripts/docs_index.py ingest                 # (re)build the index
    python scripts/docs_index.py search "task billing code DFF" -k 5
    python scripts/docs_index.py dff --filter task      # list ATTRIBUTEn mappings found
    python scripts/docs_index.py status                 # new / changed / removed files

Library location: ./docs-library by default, or $BIP_DOCS_DIR, or --dir PATH
(e.g. a OneDrive/SharePoint-synced folder). The index is written to
<library>/.index/index.json. Supported: .md .txt .docx .pdf .xlsx .xlsm .csv

Retrieval is BM25 over section/table chunks - no external services, no
embeddings - so it runs anywhere Claude Code runs. Every hit carries a
citation (file > section) that the agent must quote.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import os
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fsd_to_json  # noqa: E402  (reuse the docx/pdf/markdown extractors)

ROOT = Path(__file__).resolve().parent.parent
SUPPORTED = {".md", ".markdown", ".txt", ".docx", ".pdf", ".xlsx", ".xlsm", ".csv"}
INDEX_REL = Path(".index") / "index.json"
MAX_TEXT_CHARS = 1200
TABLE_ROWS_PER_CHUNK = 25
DFF_RE = re.compile(r"\bATTRIBUTE(?:_(?:CHAR|NUMBER|DATE|TIMESTAMP))?\d+\b", re.I)


def default_dir() -> Path:
    env = os.environ.get("BIP_DOCS_DIR")
    return Path(env) if env else ROOT / "docs-library"


# ---------------------------------------------------------------------------
# Extraction -> blocks (same block format as fsd_to_json)
# ---------------------------------------------------------------------------
def _cell(v: Any) -> str:
    if v is None:
        return ""
    if isinstance(v, float) and v.is_integer():
        v = int(v)
    return fsd_to_json._clean(str(v))


def _rows_to_table_block(rows: Iterable[Iterable[Any]]) -> Optional[dict]:
    clean = [[_cell(c) for c in r] for r in rows]
    clean = [r for r in clean if any(r)]
    if not clean:
        return None
    return {"type": "table", "rows": clean}


def extract_xlsx(path: Path) -> list[dict]:
    try:
        import openpyxl
    except ImportError as exc:  # pragma: no cover - environment dependent
        raise RuntimeError("openpyxl is required for .xlsx files: pip install openpyxl") from exc
    wb = openpyxl.load_workbook(str(path), read_only=True, data_only=True)
    blocks: list[dict] = []
    try:
        for ws in wb.worksheets:
            table = _rows_to_table_block(ws.iter_rows(values_only=True))
            if table:
                blocks.append({"type": "heading", "level": 1, "text": f"Sheet: {ws.title}"})
                blocks.append(table)
    finally:
        wb.close()
    return blocks


def extract_csv(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8-sig") as fh:
        table = _rows_to_table_block(csv.reader(fh))
    return [table] if table else []


def extract_blocks(path: Path) -> list[dict]:
    suffix = path.suffix.lower()
    if suffix == ".docx":
        return fsd_to_json.extract_docx(path)
    if suffix == ".pdf":
        return fsd_to_json.extract_pdf(path)
    if suffix in {".xlsx", ".xlsm"}:
        return extract_xlsx(path)
    if suffix == ".csv":
        return extract_csv(path)
    return fsd_to_json.extract_markdown(path.read_text(encoding="utf-8", errors="replace"))


# ---------------------------------------------------------------------------
# Chunking
# ---------------------------------------------------------------------------
def chunk_blocks(blocks: list[dict], rel: str) -> list[dict]:
    chunks: list[dict] = []
    path: list[tuple[int, str]] = []  # heading stack (level, text)
    buf: list[str] = []

    def section() -> str:
        return " > ".join(t for _, t in path)

    def add(kind: str, text: str, rows: Optional[list[dict]] = None) -> None:
        chunk = {"id": f"{rel}#{len(chunks) + 1}", "file": rel, "section": section(),
                 "kind": kind, "text": text}
        if rows is not None:
            chunk["rows"] = rows
        chunks.append(chunk)

    def flush() -> None:
        if buf:
            add("text", "\n".join(buf))
            buf.clear()

    for b in blocks:
        if b["type"] == "heading":
            flush()
            while path and path[-1][0] >= b["level"]:
                path.pop()
            path.append((b["level"], b["text"]))
        elif b["type"] == "paragraph":
            if buf and sum(len(x) for x in buf) + len(b["text"]) > MAX_TEXT_CHARS:
                flush()
            buf.append(b["text"])
        elif b["type"] == "table":
            flush()
            header, *body = b["rows"]
            header = [h or f"col{i + 1}" for i, h in enumerate(header)]
            if not body:  # single-row table: treat as text
                add("text", " | ".join(header))
                continue
            for start in range(0, len(body), TABLE_ROWS_PER_CHUNK):
                part = body[start:start + TABLE_ROWS_PER_CHUNK]
                rows = [{h: (r[i] if i < len(r) else "") for i, h in enumerate(header)} for r in part]
                lines = ["Table: " + " | ".join(header)]
                lines += [" | ".join(f"{k}: {v}" for k, v in row.items() if v) for row in rows]
                add("table", "\n".join(lines), rows)
    flush()
    return chunks


# ---------------------------------------------------------------------------
# Index
# ---------------------------------------------------------------------------
def iter_docs(docs_dir: Path) -> Iterable[Path]:
    for p in sorted(docs_dir.rglob("*")):
        rel_parts = p.relative_to(docs_dir).parts
        if any(part.startswith(".") for part in rel_parts):
            continue
        if p.is_file() and p.suffix.lower() in SUPPORTED and p.name.lower() != "readme.md":
            yield p


def build_index(docs_dir: Path) -> dict:
    files: dict[str, dict] = {}
    chunks: list[dict] = []
    errors: dict[str, str] = {}
    for p in iter_docs(docs_dir):
        rel = p.relative_to(docs_dir).as_posix()
        try:
            file_chunks = chunk_blocks(extract_blocks(p), rel)
        except Exception as exc:  # keep indexing other files
            errors[rel] = f"{type(exc).__name__}: {exc}"
            continue
        st = p.stat()
        files[rel] = {"mtime": st.st_mtime, "size": st.st_size, "chunks": len(file_chunks)}
        chunks.extend(file_chunks)
    return {"version": 1, "files": files, "errors": errors, "chunks": chunks}


def index_path(docs_dir: Path) -> Path:
    return docs_dir / INDEX_REL


def save_index(docs_dir: Path, index: dict) -> Path:
    out = index_path(docs_dir)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(index, indent=1, ensure_ascii=False), encoding="utf-8")
    return out


def load_index(docs_dir: Path) -> dict:
    p = index_path(docs_dir)
    if not p.is_file():
        raise FileNotFoundError(f"no index at {p} - run: python scripts/docs_index.py ingest")
    return json.loads(p.read_text(encoding="utf-8"))


def status(docs_dir: Path, index: dict) -> dict[str, list[str]]:
    on_disk = {p.relative_to(docs_dir).as_posix(): p for p in iter_docs(docs_dir)}
    indexed = index.get("files", {})
    new = sorted(set(on_disk) - set(indexed))
    removed = sorted(set(indexed) - set(on_disk))
    changed = sorted(r for r in set(on_disk) & set(indexed)
                     if abs(on_disk[r].stat().st_mtime - indexed[r]["mtime"]) > 1e-6
                     or on_disk[r].stat().st_size != indexed[r]["size"])
    return {"new": new, "changed": changed, "removed": removed}


# ---------------------------------------------------------------------------
# Search (BM25)
# ---------------------------------------------------------------------------
def tokenize(text: str) -> list[str]:
    tokens = []
    for tok in re.findall(r"[a-z0-9_]+", text.lower()):
        tokens.append(tok)
        if "_" in tok:
            tokens.extend(t for t in tok.split("_") if t)
    return tokens


def search(index: dict, query: str, k: int = 8, k1: float = 1.5, b: float = 0.75) -> list[dict]:
    chunks = index.get("chunks", [])
    if not chunks:
        return []
    docs = [tokenize(c["section"] + "\n" + c["text"]) for c in chunks]
    n = len(docs)
    avgdl = sum(len(d) for d in docs) / n or 1.0
    df: Counter = Counter()
    for d in docs:
        df.update(set(d))
    q_terms = list(dict.fromkeys(tokenize(query)))
    results = []
    for chunk, d in zip(chunks, docs):
        tf = Counter(d)
        score = 0.0
        for t in q_terms:
            if t not in tf:
                continue
            idf = math.log(1 + (n - df[t] + 0.5) / (df[t] + 0.5))
            score += idf * tf[t] * (k1 + 1) / (tf[t] + k1 * (1 - b + b * len(d) / avgdl))
        if score > 0:
            results.append((score, chunk))
    results.sort(key=lambda x: -x[0])
    out = []
    for score, chunk in results[:k]:
        out.append({"score": round(score, 3), "citation": cite(chunk), "id": chunk["id"],
                    "snippet": snippet(chunk["text"], q_terms), "text": chunk["text"]})
    return out


def cite(chunk: dict) -> str:
    return f"{chunk['file']} > {chunk['section']}" if chunk["section"] else chunk["file"]


def snippet(text: str, q_terms: list[str], max_lines: int = 4) -> str:
    lines = text.splitlines()
    qs = set(q_terms)
    hits = [ln for ln in lines if qs & set(tokenize(ln))]
    chosen = (hits or lines)[:max_lines]
    return "\n".join(ln if len(ln) <= 300 else ln[:297] + "..." for ln in chosen)


# ---------------------------------------------------------------------------
# DFF extraction
# ---------------------------------------------------------------------------
def find_dff(index: dict, filters: Iterable[str] = ()) -> list[dict]:
    """Rows / lines that mention an ATTRIBUTEn column, with citation."""
    terms = [f.lower() for f in filters if f]
    hits = []
    for chunk in index.get("chunks", []):
        if chunk["kind"] == "table":
            for row in chunk.get("rows", []):
                cols = sorted({m.group(0).upper() for v in row.values() for m in DFF_RE.finditer(v)})
                if not cols:
                    continue
                haystack = (chunk["section"] + " " + " ".join(row.values())).lower()
                if all(t in haystack for t in terms):
                    hits.append({"citation": cite(chunk), "columns": cols, "row": row})
        else:
            for line in chunk["text"].splitlines():
                cols = sorted({m.group(0).upper() for m in DFF_RE.finditer(line)})
                if not cols:
                    continue
                haystack = (chunk["section"] + " " + line).lower()
                if all(t in haystack for t in terms):
                    hits.append({"citation": cite(chunk), "columns": cols, "line": line})
    return hits


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Local RAG index over configuration documents")
    ap.add_argument("--dir", type=Path, default=None, help="docs library (default: $BIP_DOCS_DIR or ./docs-library)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("ingest", help="(re)build the index")
    sp = sub.add_parser("search", help="search the index")
    sp.add_argument("query")
    sp.add_argument("-k", type=int, default=8)
    sp.add_argument("--json", action="store_true")
    sp.add_argument("--full", action="store_true", help="print the whole chunk, not a snippet")
    dp = sub.add_parser("dff", help="list DFF ATTRIBUTEn mappings found in the docs")
    dp.add_argument("--filter", action="append", default=[], help="term that must appear (repeatable)")
    dp.add_argument("--json", action="store_true")
    sub.add_parser("status", help="show new / changed / removed files since the last ingest")
    args = ap.parse_args(argv)

    docs_dir = (args.dir or default_dir()).resolve()
    if not docs_dir.is_dir():
        print(f"error: docs library {docs_dir} does not exist", file=sys.stderr)
        return 2

    if args.cmd == "ingest":
        index = build_index(docs_dir)
        out = save_index(docs_dir, index)
        print(f"indexed {len(index['files'])} file(s), {len(index['chunks'])} chunk(s) -> {out}")
        for rel, err in index["errors"].items():
            print(f"  skipped {rel}: {err}", file=sys.stderr)
        return 0

    try:
        index = load_index(docs_dir)
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if args.cmd == "status":
        st = status(docs_dir, index)
        for key in ("new", "changed", "removed"):
            print(f"{key}: {', '.join(st[key]) or '-'}")
        if any(st.values()):
            print("run: python scripts/docs_index.py ingest")
        return 0

    if args.cmd == "search":
        hits = search(index, args.query, k=args.k)
        if args.json:
            print(json.dumps(hits, indent=2, ensure_ascii=False))
        elif not hits:
            print("no matches")
        else:
            for i, h in enumerate(hits, 1):
                print(f"[{i}] {h['citation']}  (score {h['score']})")
                body = h["text"] if args.full else h["snippet"]
                print("    " + body.replace("\n", "\n    ") + "\n")
        return 0

    if args.cmd == "dff":
        hits = find_dff(index, args.filter)
        if args.json:
            print(json.dumps(hits, indent=2, ensure_ascii=False))
        elif not hits:
            print("no ATTRIBUTEn mappings found")
        else:
            for h in hits:
                detail = h.get("line") or " | ".join(f"{k}: {v}" for k, v in h["row"].items() if v)
                print(f"{', '.join(h['columns'])}  <- {h['citation']}\n    {detail}")
        return 0
    return 2  # pragma: no cover


if __name__ == "__main__":
    sys.exit(main())
