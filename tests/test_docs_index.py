import json
import shutil

import pytest

import docs_index
from conftest import ROOT

SAMPLES = ROOT / "docs-library" / "samples"


@pytest.fixture
def library(tmp_path):
    lib = tmp_path / "lib"
    shutil.copytree(SAMPLES, lib)
    (lib / "README.md").write_text("# readme is not indexed\nATTRIBUTE99", encoding="utf-8")
    (lib / ".hidden").mkdir()
    (lib / ".hidden" / "skip.md").write_text("# hidden\nATTRIBUTE98", encoding="utf-8")
    return lib


@pytest.fixture
def index(library):
    idx = docs_index.build_index(library)
    docs_index.save_index(library, idx)
    return idx


def test_ingest_indexes_supported_files_only(index):
    assert set(index["files"]) == {"sample-ppm-dff-configuration.md", "sample-value-set-billing-codes.csv"}
    assert index["errors"] == {}
    assert all(c["file"] in index["files"] for c in index["chunks"])


def test_table_rows_are_structured(index):
    dff_chunk = next(c for c in index["chunks"]
                     if c["kind"] == "table" and "Project Task Descriptive Flexfield" in c["section"])
    assert dff_chunk["rows"][0]["Segment Name"] == "BILLING_CODE"
    assert dff_chunk["rows"][0]["Table Column"] == "ATTRIBUTE1"
    assert dff_chunk["section"].endswith("1. Project Task Descriptive Flexfield")


def test_search_finds_billing_code_with_citation(index):
    hits = docs_index.search(index, "task billing code flexfield column", k=3)
    assert hits
    top = hits[0]
    assert top["citation"].startswith("sample-ppm-dff-configuration.md > ")
    assert "ATTRIBUTE1" in top["text"]
    assert "Billing Code" in top["snippet"]


def test_search_underscore_tokens(index):
    hits = docs_index.search(index, "EX_TASK_BILLING_CODE BC-900", k=2)
    assert any(h["citation"] == "sample-value-set-billing-codes.csv" for h in hits)


def test_search_no_match(index):
    assert docs_index.search(index, "zzzz_unrelated_term") == []


def test_dff_extraction_and_filter(index):
    hits = docs_index.find_dff(index)
    cols = sorted(c for h in hits for c in h["columns"])
    assert cols.count("ATTRIBUTE9") >= 2  # context-dependent: two rows + the note
    assert "ATTRIBUTE99" not in cols and "ATTRIBUTE98" not in cols  # README / hidden skipped
    billing = docs_index.find_dff(index, ["billing"])
    assert [h["columns"] for h in billing if "row" in h] == [["ATTRIBUTE1"]]
    assert billing[0]["row"]["Global"] == "Yes"


def test_status_detects_changes(library, index):
    assert docs_index.status(library, index) == {"new": [], "changed": [], "removed": []}
    (library / "new.txt").write_text("hello", encoding="utf-8")
    (library / "sample-value-set-billing-codes.csv").unlink()
    st = docs_index.status(library, index)
    assert st["new"] == ["new.txt"] and st["removed"] == ["sample-value-set-billing-codes.csv"]


def test_xlsx_ingest(tmp_path):
    openpyxl = pytest.importorskip("openpyxl")
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Task DFF"
    ws.append(["Context", "Segment", "Column"])
    ws.append(["Global Data Elements", "Billing Code", "ATTRIBUTE1"])
    ws.append([None, None, None])
    ws.append(["FIELD_WORK", "Site Code", "ATTRIBUTE9"])
    lib = tmp_path / "x"
    lib.mkdir()
    wb.save(str(lib / "config.xlsx"))
    idx = docs_index.build_index(lib)
    chunk = next(c for c in idx["chunks"] if c["kind"] == "table")
    assert chunk["section"] == "Sheet: Task DFF"
    assert len(chunk["rows"]) == 2  # empty row skipped
    assert docs_index.find_dff(idx, ["site"])[0]["columns"] == ["ATTRIBUTE9"]


def test_bad_file_is_reported_not_fatal(tmp_path):
    lib = tmp_path / "lib"
    lib.mkdir()
    (lib / "broken.docx").write_bytes(b"not a zip")
    (lib / "ok.md").write_text("# Roles\nClient Contact role", encoding="utf-8")
    idx = docs_index.build_index(lib)
    assert "broken.docx" in idx["errors"]
    assert "ok.md" in idx["files"]


def test_cli(library, capsys):
    assert docs_index.main(["--dir", str(library), "ingest"]) == 0
    assert "indexed 2 file(s)" in capsys.readouterr().out
    assert docs_index.main(["--dir", str(library), "search", "client contact role", "--json"]) == 0
    hits = json.loads(capsys.readouterr().out)
    assert "2. Project Roles" in hits[0]["citation"]
    assert docs_index.main(["--dir", str(library), "dff", "--filter", "billing"]) == 0
    assert "ATTRIBUTE1" in capsys.readouterr().out
    assert docs_index.main(["--dir", str(library), "status"]) == 0


def test_cli_missing_index_and_dir(tmp_path):
    assert docs_index.main(["--dir", str(tmp_path), "search", "x"]) == 2
    assert docs_index.main(["--dir", str(tmp_path / "nope"), "ingest"]) == 2
