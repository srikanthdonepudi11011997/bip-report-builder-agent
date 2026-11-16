import json

import pytest

import sql_lint
from conftest import EXAMPLE_DIR
from sql_lint import ERROR, WARNING, lint_sql, mask_sql


def rules(findings):
    return sorted(f.rule for f in findings)


def spec_with(params=(), columns=()):
    return {"parameters": list(params), "columns": list(columns)}


def param(bind, type_="string", multi=True, **extra):
    return {"bind": bind, "label": bind, "type": type_, "multi_select": multi, "required": False, **extra}


# ---------------------------------------------------------------- masking
def test_mask_preserves_length_and_lines():
    sql = "select 'a--b' x -- comment :p_hidden\nfrom t /* :p_also\n hidden */ where y = ':p_str'"
    code, code_ns = mask_sql(sql)
    assert len(code) == len(sql) == len(code_ns)
    assert code.count("\n") == sql.count("\n")
    assert ":p_hidden" not in code and ":p_also" not in code
    assert "'a--b'" in code  # '--' inside a string is not a comment
    assert ":p_str" in code and ":p_str" not in code_ns


def test_binds_in_comments_and_strings_are_ignored():
    sql = """
    -- WHERE x IN (:p_commented)
    SELECT TO_CHAR(SYSDATE, 'HH24:MI') AS run_time FROM dual
    """
    assert lint_sql(sql) == []


# ---------------------------------------------------------------- BIP001
def test_bip001_multiselect_without_guard():
    sql = "SELECT a.x AS x FROM t a WHERE a.name IN (:p_name)"
    f = lint_sql(sql)
    assert rules(f) == ["BIP001"]
    assert f[0].severity == ERROR and f[0].line == 1


def test_bip001_with_guard_passes():
    sql = "SELECT a.x AS x FROM t a WHERE (COALESCE(:p_name, NULL) IS NULL OR a.name IN (:p_name))"
    assert lint_sql(sql) == []


def test_bip001_skipped_for_single_select_spec_param():
    sql = "SELECT a.x AS x FROM t a WHERE (:p_flag IS NULL OR a.flag IN (:p_flag))"
    spec = spec_with([param(":p_flag", multi=False)], [{"seq": 1, "alias": "X", "header": "X"}])
    assert lint_sql(sql, spec) == []


# ---------------------------------------------------------------- BIP002
def test_bip002_numeric_id_without_to_char():
    sql = "SELECT a.x AS x FROM t a WHERE (COALESCE(:p_proj, NULL) IS NULL OR a.project_id IN (:p_proj))"
    assert rules(lint_sql(sql)) == ["BIP002"]


def test_bip002_with_to_char_passes():
    sql = ("SELECT a.x AS x FROM t a WHERE (COALESCE(:p_proj, NULL) IS NULL "
           "OR TO_CHAR(a.project_id) IN (:p_proj))")
    assert lint_sql(sql) == []


def test_bip002_equals_uses_spec_type():
    sql = "SELECT a.x AS x FROM t a WHERE a.org_id = :p_org"
    cols = [{"seq": 1, "alias": "X", "header": "X"}]
    assert rules(lint_sql(sql, spec_with([param(":p_org", multi=False)], cols))) == ["BIP002"]
    assert lint_sql(sql, spec_with([param(":p_org", type_="number", multi=False)], cols)) == []


# ---------------------------------------------------------------- BIP003
def test_bip003_date_without_trunc():
    sql = "SELECT a.x AS x FROM t a WHERE a.start_date >= :p_date_from"
    f = lint_sql(sql)
    assert rules(f) == ["BIP003"]


def test_bip003_trunc_and_null_check_pass():
    sql = ("SELECT a.x AS x FROM t a WHERE (:p_date_from IS NULL "
           "OR TRUNC(a.start_date) >= TRUNC(:p_date_from)) "
           "AND TRUNC(a.end_date) <= TRUNC(NVL(:p_date_to, SYSDATE))")
    assert lint_sql(sql) == []


def test_bip003_uses_spec_types():
    sql = "SELECT a.x AS x FROM t a WHERE a.d >= :p_from"
    spec = spec_with([param(":p_from", type_="date", multi=False)], [{"seq": 1, "alias": "X", "header": "X"}])
    assert rules(lint_sql(sql, spec)) == ["BIP003"]


# ---------------------------------------------------------------- BIP004
def test_bip004_tl_without_language():
    sql = "SELECT s.name AS x FROM pjf_project_statuses_tl s"
    assert rules(lint_sql(sql)) == ["BIP004"]


def test_bip004_tl_with_language_passes():
    sql = ("SELECT s.name AS x FROM pjf_projects_all_b p "
           "JOIN pjf_projects_all_tl s ON s.project_id = p.project_id AND s.language = USERENV('LANG')")
    assert lint_sql(sql) == []


def test_bip004_reversed_comparison_and_no_alias():
    assert lint_sql("SELECT name AS x FROM foo_tl WHERE USERENV('LANG') = language") == []
    assert lint_sql("SELECT t.name AS x FROM foo_tl t WHERE USERENV('LANG') = t.language") == []
    assert rules(lint_sql("SELECT name AS x FROM foo_tl WHERE 1 = 1")) == ["BIP004"]


def test_bip004_language_on_other_alias_does_not_count():
    sql = ("SELECT a.name AS x FROM a_tl a JOIN b_tl b ON b.id = a.id "
           "WHERE a.language = USERENV('LANG')")
    f = lint_sql(sql)
    assert rules(f) == ["BIP004"]
    assert "b_tl b" in f[0].message


# ---------------------------------------------------------------- BIP005/006
def test_bip005_forbidden_object():
    sql = "SELECT c.project_id AS x FROM pjf_project_customers c"
    f = lint_sql(sql)
    assert rules(f) == ["BIP005"]
    assert "PJF_PROJECT_PARTIES" in f[0].message


def test_bip005_ignored_in_comment():
    assert lint_sql("-- not pjf_project_customers\nSELECT 1 AS x FROM dual") == []


def test_bip006_select_star():
    f = lint_sql("SELECT * FROM dual")
    assert rules(f) == ["BIP006"]
    assert f[0].severity == WARNING


# ---------------------------------------------------------------- BIP007
def test_bip007_placeholder_reported_once_per_token():
    sql = ("SELECT 1 AS x FROM t WHERE a = {{ROLE_ID}}\n"
           "AND b = {{ROLE_ID}} -- {{IN_COMMENT_IS_FINE}}\nAND c = {{OTHER}}")
    f = lint_sql(sql)
    assert rules(f) == ["BIP007", "BIP007"]
    assert [x.line for x in f] == [1, 3]


# ---------------------------------------------------------------- BIP008/009/011
def test_spec_coverage_rules():
    sql = "SELECT a.x AS x_col FROM t a WHERE (:p_used IS NULL OR a.y = :p_used) AND a.z = :p_extra"
    spec = spec_with(
        [param(":p_used", multi=False), param(":p_unused", multi=False)],
        [{"seq": 1, "alias": "X_COL", "header": "X"}, {"seq": 2, "alias": "MISSING", "header": "Missing"}],
    )
    assert rules(lint_sql(sql, spec)) == ["BIP008", "BIP009", "BIP011"]


def test_alias_match_is_whole_word():
    spec = spec_with([], [{"seq": 1, "alias": "TASK", "header": "Task"}])
    assert rules(lint_sql("SELECT t.n AS task_name FROM t", spec)) == ["BIP011"]
    assert lint_sql('SELECT t.n AS "TASK" FROM t', spec) == []


# ---------------------------------------------------------------- BIP010
def test_bip010_hardcoded_id():
    assert rules(lint_sql("SELECT 1 AS x FROM t WHERE r = 300000012345678")) == ["BIP010"]
    assert lint_sql("SELECT 1 AS x FROM t WHERE r = 300000012345678 -- client role") == []


def test_bip010_string_on_line_is_not_a_comment():
    sql = "SELECT 1 AS x FROM t WHERE r = 300000012345678 AND s = 'A'"
    assert rules(lint_sql(sql)) == ["BIP010"]


# ---------------------------------------------------------------- suppression
def test_inline_suppression_and_disable():
    sql = "SELECT * FROM dual -- lint: disable=BIP006"
    assert lint_sql(sql) == []
    assert lint_sql("SELECT * FROM dual", disabled=["BIP006"]) == []


# ---------------------------------------------------------------- example + CLI
def test_example_data_model_has_no_errors():
    spec = json.loads((EXAMPLE_DIR / "02-spec.json").read_text(encoding="utf-8"))
    sql = (EXAMPLE_DIR / "04-data-model.sql").read_text(encoding="utf-8")
    findings = lint_sql(sql, spec)
    assert [f for f in findings if f.severity == ERROR] == []
    # the public example leaves its 2 role-ID tokens unresolved (IDs are instance-specific)
    assert rules(findings) == ["BIP007"] * 2


def test_example_lov_queries_have_no_errors():
    sql = (EXAMPLE_DIR / "05-lov-queries.sql").read_text(encoding="utf-8")
    findings = lint_sql(sql)
    assert rules(findings) == ["BIP007"]


def test_cli_exit_codes(tmp_path, capsys):
    bad = tmp_path / "bad.sql"
    bad.write_text("SELECT c.x AS x FROM pjf_project_customers c", encoding="utf-8")
    good = tmp_path / "good.sql"
    good.write_text("SELECT 1 AS x FROM dual", encoding="utf-8")

    assert sql_lint.main([str(good)]) == 0
    assert sql_lint.main([str(bad)]) == 1
    assert sql_lint.main([str(bad), "--format", "json"]) == 1
    out = capsys.readouterr().out
    payload = json.loads(out[out.index("{"):])
    assert payload["errors"] == 1 and payload["findings"][0]["rule"] == "BIP005"


def test_cli_strict_and_list_rules(tmp_path, capsys):
    warn = tmp_path / "warn.sql"
    warn.write_text("SELECT * FROM dual", encoding="utf-8")
    assert sql_lint.main([str(warn)]) == 0
    assert sql_lint.main([str(warn), "--strict"]) == 1
    assert sql_lint.main(["--list-rules"]) == 0
    assert "BIP011" in capsys.readouterr().out


def test_cli_with_spec(capsys):
    rc = sql_lint.main([str(EXAMPLE_DIR / "04-data-model.sql"), "--spec", str(EXAMPLE_DIR / "02-spec.json")])
    assert rc == 0
    assert "0 error(s), 2 warning(s)" in capsys.readouterr().out


@pytest.mark.parametrize("rule", sorted(sql_lint.RULES))
def test_every_rule_is_documented_in_readme(rule):
    readme = (EXAMPLE_DIR.parent.parent / "README.md").read_text(encoding="utf-8")
    assert rule in readme
