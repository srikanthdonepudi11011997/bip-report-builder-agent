import json

import pytest

import fsd_to_json
from conftest import EXAMPLE_DIR


def test_markdown_example_fsd():
    doc = fsd_to_json.convert(EXAMPLE_DIR / "fsd-input.md")
    assert doc["format"] == "markdown"
    assert doc["source"] == "fsd-input.md"  # file name only, never a full path

    hints = doc["hints"]
    assert hints["report_id"] == "RPT-PPM-001"
    assert hints["title"] == "Project Task Listing"
    assert hints["module"].startswith("Project Portfolio Management")

    assert len(hints["parameter_tables"]) == 1
    params = doc["tables"][hints["parameter_tables"][0]]
    assert params["header"][1] == "Parameter"
    assert len(params["rows"]) == 7
    assert params["rows"][4][1] == "Project Start Date From"

    assert len(hints["column_tables"]) == 1
    cols = doc["tables"][hints["column_tables"][0]]
    assert len(cols["rows"]) == 11
    assert cols["rows"][-1][1] == "Chargeable"

    headings = [s["heading"] for s in doc["sections"]]
    assert "5. Filters and Business Rules" in headings


def test_markdown_separator_rows_skipped():
    blocks = fsd_to_json.extract_markdown("| a | b |\n|---|:---:|\n| 1 | 2 |\n\ntext")
    assert blocks[0] == {"type": "table", "rows": [["a", "b"], ["1", "2"]]}
    assert blocks[1] == {"type": "paragraph", "text": "text"}


def test_report_id_free_text_fallback():
    doc = fsd_to_json.build_document(
        [{"type": "paragraph", "text": "This FSD covers Report ID: GL-042 for month end."}], "x.md", "markdown")
    assert doc["hints"]["report_id"] == "GL-042"


def test_docx_extraction(tmp_path):
    docx = pytest.importorskip("docx")
    d = docx.Document()
    d.add_heading("Functional Specification", level=1)
    t = d.add_table(rows=2, cols=2)
    t.cell(0, 0).text, t.cell(0, 1).text = "Report ID", "RPT-HCM-007"
    t.cell(1, 0).text, t.cell(1, 1).text = "Report Name", "Headcount by Department"
    d.add_heading("Parameters", level=2)
    p = d.add_table(rows=3, cols=4)
    for c, v in enumerate(["Parameter", "Type", "Mandatory", "Multi-select"]):
        p.cell(0, c).text = v
    for c, v in enumerate(["As of Date", "Date", "Y", "N"]):
        p.cell(1, c).text = v
    for c, v in enumerate(["Department", "Text", "Y", "Y"]):
        p.cell(2, c).text = v
    d.add_paragraph("Show active employees only.")
    path = tmp_path / "spec.docx"
    d.save(str(path))

    doc = fsd_to_json.convert(path)
    assert doc["format"] == "docx"
    assert doc["hints"]["report_id"] == "RPT-HCM-007"
    assert doc["hints"]["title"] == "Headcount by Department"
    assert doc["hints"]["parameter_tables"] == [1]
    ptab = doc["tables"][1]
    assert ptab["section"] == "Parameters"
    # adjacent equal values ("Y", "Y") must NOT be collapsed
    assert ptab["rows"][1] == ["Department", "Text", "Y", "Y"]
    params_section = next(s for s in doc["sections"] if s["heading"] == "Parameters")
    assert "active employees" in params_section["text"]


def test_unsupported_extension(tmp_path):
    path = tmp_path / "spec.xlsx"
    path.write_text("x", encoding="utf-8")
    with pytest.raises(ValueError):
        fsd_to_json.convert(path)
    assert fsd_to_json.main([str(path)]) == 2


def test_cli_writes_output(tmp_path, capsys):
    out = tmp_path / "out" / "01-fsd-raw.json"
    assert fsd_to_json.main([str(EXAMPLE_DIR / "fsd-input.md"), "-o", str(out)]) == 0
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["hints"]["report_id"] == "RPT-PPM-001"
    assert "report_id='RPT-PPM-001'" in capsys.readouterr().out
