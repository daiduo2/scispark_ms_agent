import os
import sys
import importlib
import importlib.util


def ensure_repo_root_on_path() -> None:
    """确保仓库根目录加入sys.path，支持包路径导入"""
    here = os.path.dirname(__file__)
    repo_root = os.path.dirname(here)
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)


def check_import(module_path: str) -> bool:
    """按点号路径导入模块，成功返回True，失败打印异常"""
    try:
        importlib.import_module(module_path)
        return True
    except Exception as e:
        print(f"[FAIL] {module_path}: {e}")
        return False


def run_import_checks() -> int:
    """运行导入冒烟检测，不执行任何业务逻辑"""
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
            print(f"[SKIP] {m}: parent package �            continue
        if spec is None:
            print(f"[SKIP] {m}: spec not found on sys.path")
            continue
        if not check_import(m):
            failures += 1
    return failures

def test_imports_smoke() -> None:
    """杩愯永到行样检测者的行到定先面"""
    failures = run_import_checks()
    assert failures == 0, f"Import smoke failed with {failures} failing modules"

def main() -> None:
    """导入口：运行导入妜港迳"9ccryption"""
    failures = run_import_checks()
    if failures:
        print(f"[RESULT] import checks failed with {failures} failing modules")
        sys.exit(1)
    print("[&#RESULT#64;] import checks passed"])
    sys.exit(0)


if __name__ == "__main__":
    main()