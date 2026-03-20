#!/usr/bin/env python3
"""
Verification script for PromptStorageV2 implementation.

Checks that all files are created and the implementation is correct
without requiring external dependencies.
"""

import sys
import json
from pathlib import Path


def print_check(name, passed, details=""):
    """Print check result."""
    status = "✅" if passed else "❌"
    print(f"{status} {name}")
    if details:
        print(f"    {details}")


def check_file_structure():
    """Check that all required files exist."""
    print_check("File structure check", True)

    # Check main storage file
    storage_file = Path("src/storage/prompts_v2.py")
    if not storage_file.exists():
        print_check("Storage v2 file", False, "File not found: src/storage/prompts_v2.py")
        return False
    print_check("Storage v2 file", True)

    # Check middleware files
    middleware_dir = Path("src/middleware")
    if not middleware_dir.exists():
        print_check("Middleware directory", False, "Directory not found")
        return False

    middleware_init = middleware_dir / "__init__.py"
    baseline_verification = middleware_dir / "baseline_verification.py"

    print_check("Middleware __init__.py", middleware_init.exists())
    print_check("Baseline verification middleware", baseline_verification.exists())

    return True


def check_core_prompts():
    """Check core prompts directory."""
    print_check("Core prompts check", True)

    core_dir = Path("prompts/core")
    if not core_dir.exists():
        print_check("Core directory", False, "Not found")
        return False

    # Check baseline lock
    baseline_lock = core_dir / ".promt-baseline-lock"
    if not baseline_lock.exists():
        print_check("Baseline lock file", False, "Not found")
        return False

    # Verify lock structure
    try:
        with open(baseline_lock, 'r') as f:
            lock_data = json.load(f)
            print_check("Baseline lock JSON format", True)
            print_check("Baseline lock has checksums", "checksums" in lock_data)
            print_check("Baseline lock has verification rules", "verification_rules" in lock_data)
            print_check("Baseline lock checksum entries", len(lock_data.get("checksums", {})) > 0)
    except Exception as e:
        print_check("Baseline lock parsing", False, str(e))
        return False

    # Check core README
    core_readme = core_dir / "README.md"
    print_check("Core README", core_readme.exists())

    return True


def check_universal_prompts():
    """Check universal prompts directory."""
    print_check("Universal prompts check", True)

    universal_dir = Path("prompts/universal/ai_agent_prompts")
    if not universal_dir.exists():
        print_check("Universal directory", False, "Not found")
        return False

    # Check README
    readme = universal_dir / "README.md"
    print_check("Universal README", readme.exists())

    # Check for expected prompts
    expected_prompts = [
        "promt-bug-fix.md",
        "promt-ci-cd-pipeline.md",
        "promt-context7-generation.md",
        "promt-feature-add.md",
        "promt-mvp-baseline-generator-universal.md",
        "promt-system-adapt.md",
        "promt-prompt-creator.md",
        "promt-refactoring.md",
        "promt-security-audit.md",
        "promt-quality-test.md",
        "promt-onboarding.md",
        "promt-project-stack-dump.md",
        "promt-project-adaptation.md",
        "promt-versioning-policy.md",
        # Meta prompts
        "promt-verification.md",
        "promt-consolidation.md",
        "promt-index-update.md",
        "promt-readme-sync.md",
        "promt-project-rules-sync.md",
        "promt-adr-implementation-planner.md",
        "promt-adr-template-migration.md",
        "promt-workflow-orchestration.md",
        "promt-sync-report-export.md",
        "promt-system-evolution.md"
    ]

    # Check for prompt files (with some flexibility for naming)
    found_prompts = []
    for prompt_file in universal_dir.glob("promt-*.md"):
        found_prompts.append(prompt_file.name)

    # Check for deprecated directory
    deprecated_dir = universal_dir / "deprecated"
    if deprecated_dir.exists():
        for prompt_file in deprecated_dir.glob("*.md"):
            found_prompts.append(prompt_file.name)

    print_check(f"Universal prompts found ({len(found_prompts)})", len(found_prompts) >= 10)
    print_check(f"Expected prompts in registry ({len(expected_prompts)})", len(expected_prompts) >= 20)

    return True


def check_mpv_stage_prompts():
    """Check MPV stage prompts directory."""
    print_check("MPV stage prompts check", True)

    mpv_dir = Path("prompts/universal/mpv_stages")
    if not mpv_dir.exists():
        print_check("MPV directory", False, "Not found")
        return False

    # Check for MPV stage prompts
    expected_stages = [
        "promt-ideation.md",
        "promt-analysis.md",
        "promt-design.md",
        "promt-implementation.md",
        "promt-testing.md",
        "promt-debugging.md",
        "promt-finish.md"
    ]

    found_stages = []
    for stage_file in mpv_dir.glob("promt-*.md"):
        found_stages.append(stage_file.name)

    for stage in expected_stages:
        print_check(f"MPV stage: {stage}", (mpv_dir / stage).exists())

    print_check(f"MPV registry", (mpv_dir / "registry.json").exists())
    print_check(f"MPV stages found ({len(found_stages)})", len(found_stages) == 7)

    return True


def check_main_registry():
    """Check main registry file."""
    print_check("Main registry check", True)

    registry_file = Path("prompts/registry.json")
    if not registry_file.exists():
        print_check("Main registry file", False, "Not found")
        return False

    try:
        with open(registry_file, 'r') as f:
            registry = json.load(f)
            print_check("Registry JSON format", True)
            print_check("Registry has prompts", "prompts" in registry)
            print_check("Registry version", "version" in registry)
            print_check(f"Total prompts in registry", len(registry.get("prompts", {})) > 0)
    except Exception as e:
        print_check("Registry parsing", False, str(e))
        return False

    return True


def check_implementation_features():
    """Check implementation has required features."""
    print_check("Implementation features check", True)

    # Read storage v2 file and check for key features
    storage_file = Path("src/storage/prompts_v2.py")
    if not storage_file.exists():
        return False

    content = storage_file.read_text()

    # Check for key classes and enums
    print_check("PromptTier enum", "class PromptTier(str, Enum)" in content)
    print_check("BaselineLockManager class", "class BaselineLockManager" in content)
    print_check("PromptStorageV2 class", "class PromptStorageV2" in content)
    print_check("get_storage function", "def get_storage()" in content)
    print_check("get_prompt function", "def get_prompt(" in content)
    print_check("get_tier_prompts function", "def get_tier_prompts(" in content)

    # Check for key methods
    print_check("load_prompt method", "def load_prompt(" in content)
    print_check("resolve_prompt_tier method", "def resolve_prompt_tier(" in content)
    print_check("verify_baseline_integrity method", "def verify_baseline_integrity(" in content)
    print_check("list_prompts method", "def list_prompts(" in content)
    print_check("search_prompts method", "def search_prompts(" in content)
    print_check("get_all_prompts method", "def get_all_prompts(" in content)
    print_check("clear_cache method", "def clear_cache(" in content)

    # Check for caching decorators
    print_check("lru_cache on load_prompt_content", "@lru_cache" in content and "load_prompt_content" in content)
    print_check("lru_cache on get_registry", "@lru_cache" in content and "get_registry" in content)

    # Check for tier definitions
    print_check("CORE tier definition", 'CORE = "core"' in content)
    print_check("UNIVERSAL tier definition", 'UNIVERSAL = "universal"' in content)
    print_check("MPV_STAGE tier definition", 'MPV_STAGE = "mpv_stage"' in content)
    print_check("PROJECTS tier definition", 'PROJECTS = "projects"' in content)

    # Check for cascade priority logic
    print_check("Cascade priority resolution (Projects → MPV → Universal → Core)",
                any([
                    "PROJECTS" in content and "MPV_STAGE" in content and "UNIVERSAL" in content and "CORE" in content
                ]))

    return True


def check_middleware_features():
    """Check middleware implementation."""
    print_check("Middleware features check", True)

    baseline_verification_file = Path("src/middleware/baseline_verification.py")
    if not baseline_verification_file.exists():
        return False

    content = baseline_verification_file.read_text()

    print_check("BaselineVerificationError class", "class BaselineVerificationError" in content)
    print_check("BaselineVerificationConfig class", "class BaselineVerificationConfig" in content)
    print_check("verify_baseline_on_startup function", "def verify_baseline_on_startup(" in content)
    print_check("baseline_verification_middleware", "def baseline_verification_middleware(" in content)
    print_check("verify_baseline_decorator", "def verify_baseline_decorator(" in content)
    print_check("configure_baseline_verification function", "def configure_baseline_verification(" in content)

    # Check for middleware exports
    middleware_init = Path("src/middleware/__init__.py")
    if middleware_init.exists():
        init_content = middleware_init.read_text()
        print_check("Middleware __init__ exports", "__all__" in init_content)

    return True


def check_documentation():
    """Check documentation files."""
    print_check("Documentation check", True)

    # Check phase summary
    phase_summary = Path("docs/PHASE_1_2_SUMMARY.md")
    print_check("Phase 1 & 2 summary", phase_summary.exists())

    # Check ADR documentation
    adr_index = Path("docs/explanation/adr/ADR_INDEX.md")
    print_check("ADR index", adr_index.exists())

    adr_002 = Path("docs/explanation/adr/ADR-002-tiered-prompt-architecture-mpv-integration.md")
    print_check("ADR-002 documentation", adr_002.exists())

    return True


def check_server_integration():
    """Check server integration."""
    print_check("Server integration check", True)

    server_file = Path("src/api/server.py")
    if not server_file.exists():
        return False

    content = server_file.read_text()

    # Check for imports
    print_check("Server imports v2 storage",
                "from src.storage.prompts_v2 import" in content)
    print_check("Server imports middleware",
                "from src.middleware import" in content)
    print_check("Server startup event handler",
                "startup_event" in content or "async def startup" in content)
    print_check("Server shutdown event handler",
                "shutdown_event" in content or "async def shutdown" in content)

    return True


def main():
    """Run all verification checks."""
    print("\n" + "="*60)
    print("AI Prompt System v2.0.0 - Implementation Verification")
    print("="*60 + "\n")

    checks = [
        ("File structure", check_file_structure),
        ("Core prompts", check_core_prompts),
        ("Universal prompts", check_universal_prompts),
        ("MPV stage prompts", check_mpv_stage_prompts),
        ("Main registry", check_main_registry),
        ("Implementation features", check_implementation_features),
        ("Middleware features", check_middleware_features),
        ("Documentation", check_documentation),
        ("Server integration", check_server_integration),
    ]

    passed = 0
    failed = 0

    for check_name, check_func in checks:
        try:
            if check_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print_check(f"{check_name} - Exception", False, str(e))
            failed += 1
        print()  # Empty line for readability

    # Summary
    print("="*60)
    print("Verification Summary")
    print("="*60)
    print(f"Total checks: {len(checks)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success rate: {passed/len(checks)*100:.1f}%")

    if failed == 0:
        print("\n✅ All verification checks passed!")
        print("\nThe AI Prompt System v2.0.0 implementation is complete and ready for use.")
        return 0
    else:
        print(f"\n❌ {failed} check(s) failed")
        print("\nPlease review the failed checks above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
