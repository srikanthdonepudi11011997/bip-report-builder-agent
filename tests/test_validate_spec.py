import copy
import json

import pytest

import validate_spec
from conftest import EXAMPLE_DIR


@pytest.fixture
def spec():
    return json.loads((EXAMPLE_DIR / "02-spec.json").read_text(encoding="utf-8"))


def test_example_spec_is_valid(spec):
    pytest.importorskip("jsonschema")
    errors, schema_checked = validate_spec.validate(spec)
    assert schema_checked
    assert errors == []


def test_schema_rejects_bad_bind(spec):
    pytest.importorskip("jsonschema")
    bad = copy.deepcopy(spec)
    bad["parameters"][0]["bind"] = "p_no_colon"
    errors, _ = validate_spec.validate(bad)
    assert any("parameters/0/bind" in e for e in errors)


def test_cross_checks(spec):
    bad = copy.deepcopy(spec)
    bad["parameters"][1]["bind"] = bad["parameters"][0]["bind"]
    bad["columns"][1]["alias"] = bad["columns"][0]["alias"]
    bad["columns"][2]["seq"] = 99
    bad["sorting"].append({"alias": "NOT_A_COLUMN"})
    bad["parameters"][4]["multi_select"] = True  # a date parameter
    errors = validate_spec.cross_checks(bad)
    joined = "\n".join(errors)
    assert "duplicate parameter bind" in joined
    assert "duplicate column alias" in joined
    assert "without gaps" in joined
    assert "NOT_A_COLUMN" in joined
    assert "cannot be multi-select" in joined


def test_cli(tmp_path, spec, capsys):
    good = tmp_path / "spec.json"
    good.write_text(json.dumps(spec), encoding="utf-8")
    assert validate_spec.main([str(good)]) == 0
    assert "VALID" in capsys.readouterr().out
    broken = tmp_path / "broken.json"
    broken.write_text("{not json", encoding="utf-8")
    assert validate_spec.main([str(broken)]) == 2
