import os
import sys
import importlib
import importlib.util


def ensure_repo_root_on_path() -> None:
    # 纭繚浠撳簱鏍圭洰褰曞姞鍏ys.path锛屾敮鎸佸寘璺緞瀵煎叆
    here = os.path.dirname(__file__)
    repo_root = os.path.dirname(here)
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)


def check_import(module_path: str) -> bool:
    # 鎸夌偣鍙疯矾寰勫鍏ユā鍧楋紝鎴愬姛杩斿洖True锛屽け璐ユ墦鍗板紓甯?    try:
        importlib.import_module(module_path)
        return True
    except Exception as e:
        print(f"[FAIL] {module_path}: {e}")
        return False


def run_import_checks() -> int:
    # 杩愯瀵煎叆鍐掔儫妫€娴嬶紝涓嶆墽琛屼换浣曚笟鍔￠€昏緫
    ensure_repo_root_on_path()
    modules = []
    pkg_spec = importlib.util.find_spec("scispark_ms_skills")
    if pkg_spec is not None:
        modules.extend([
            "scispark_ms_skills.common.core.skills_registry",
            "scispark_ms_skills.common.core.config",
            "scispark_ms_skills.common.utils.tool",
            "scispark_ms_skills.skills.initial_idea.scripts.main",
            "scispark_ms_skills.skills.technical_optimization.scripts.main",
            "scispark_ms_skills.skills.moa_based_optimization.scripts.main",
            "scispark_ms_skills.skills.human_ai_collaboration.scripts.main",
            "scispark_ms_skills.skills.academic_workflow.scripts.main",
            "scispark_ms_skills.skills.academic_workflow.scripts.queue",
        ])
    modules.extend([
        "common.workflow",
        "common.core.prompt",
        "common.core.moa",
        "common.core.tpl",
        "common.utils.llm_api",
        "common.utils.arxiv_api",
        "common.utils.scholar_download",
        "common.utils.pdf_to_md",
        "common.utils.wiki_search",
    ])
    failures = 0
    for m in modules:
        try:
            spec = importlib.util.find_spec(m)
        except ModuleNotFoundError:
            print(f"[SKIP] {m}: parent package missing")
            continue
        if spec is None:
            print(f"[SKIP] {m}: spec not found on sys.path")
            continue
        if not check_import(m):
            failures += 1
    return failures


def test_imports_smoke() -> None:
    # pytest鍏ュ彛锛氭墍鏈夋ā鍧楀潎搴斿彲琚鍏?    failures = run_import_checks()
    assert failures == 0, f"Import smoke failed with {failures} failing modules"
