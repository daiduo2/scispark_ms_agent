import os
import sys
import importlib


def ensure_repo_root_on_path() -> None:
    """Ensure the repository root directory is present on sys.path."""
    here = os.path.dirname(__file__)
    repo_root = os.path.dirname(here)
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)


def check_import(module_path: str) -> bool:
    """Try to import a module by its dotted path and return success flag."""
    try:
        importlib.import_module(module_path)
        return True
    except Exception as e:
        print(f"[FAIL] {module_path}: {e}")
        return False


def run_import_checks() -> int:
    """Run import checks for common and package-path modules without executing logic."""
    ensure_repo_root_on_path()
    modules = [
        "scispark_ms_skills.common.core.skills_registry",
        # package-path skill scripts
        "scispark_ms_skills.skills.initial_idea.scripts.main",
        "scispark_ms_skills.skills.technical_optimization.scripts.main",
        "scispark_ms_skills.skills.moa_based_optimization.scripts.main",
        "scispark_ms_skills.skills.human_ai_collaboration.scripts.main",
        # top-level common modules (imported by skills)
        "common.workflow",
        "common.core.config",
        "common.core.prompt",
        "common.core.moa",
        "common.core.tpl",
        "common.utils.llm_api",
        "common.utils.tool",
        "common.utils.arxiv_api",
        "common.utils.scholar_download",
        "common.utils.pdf_to_md",
        "common.utils.wiki_search",
    ]
    failed = []
    for m in modules:
        if not check_import(m):
            failed.append(m)
    if failed:
        print("[RESULT] import checks failed")
        for m in failed:
            print(f" - {m}")
        return 1
    print("[RESULT] import checks passed")
    return 0


def main() -> None:
    """Script entrypoint to run import checks and exit with appropriate code."""
    code = run_import_checks()
    sys.exit(code)


if __name__ == "__main__":
    main()
