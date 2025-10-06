#!/usr/bin/env python3
"""
Fix Function Redefinitions (F811)
Phase 2B Subtask 2b_7

Fixes 6 function redefinition issues:
1. app/database/config.py - Remove duplicate get_chromadb_client and get_duckdb_connection
2. app/services/ai_router.py - Rename legacy _estimate_request_cost
3. app/services/progress_analytics_service.py - Remove duplicate methods (2 instances)
4. test_comprehensive_speech_validation.py - Remove duplicate asyncio import
"""

import sys
from pathlib import Path


def fix_config_duplicates():
    """Fix duplicate functions in config.py"""
    file_path = Path("app/database/config.py")
    content = file_path.read_text()

    # Remove the duplicate functions at the end
    old_code = """def get_chromadb_client():
    \"\"\"Get ChromaDB client\"\"\"
    return db_manager.chromadb_client


def get_duckdb_connection():
    \"\"\"Get DuckDB connection\"\"\"
    return db_manager.duckdb_connection"""

    new_code = (
        "# Removed duplicate functions - already defined above as FastAPI dependencies"
    )

    if old_code in content:
        content = content.replace(old_code, new_code)
        file_path.write_text(content)
        print(
            f"✅ Fixed: {file_path} - Removed duplicate get_chromadb_client and get_duckdb_connection"
        )
        return True
    else:
        print(f"⚠️  Warning: Pattern not found in {file_path}")
        return False


def fix_ai_router_duplicate():
    """Fix duplicate _estimate_request_cost in ai_router.py"""
    file_path = Path("app/services/ai_router.py")
    content = file_path.read_text()

    # Rename the first (legacy) method
    old_signature = """    async def _estimate_request_cost(
        self, provider_name: str, language: str, use_case: str
    ) -> float:
        \"\"\"Estimate cost for a request to a provider\"\"\""""

    new_signature = """    async def _estimate_request_cost_legacy(
        self, provider_name: str, language: str, use_case: str
    ) -> float:
        \"\"\"Legacy cost estimation method - kept for backward compatibility\"\"\""""

    if old_signature in content:
        content = content.replace(
            old_signature, new_signature, 1
        )  # Only replace first occurrence
        file_path.write_text(content)
        print(
            f"✅ Fixed: {file_path} - Renamed legacy _estimate_request_cost to _estimate_request_cost_legacy"
        )
        return True
    else:
        print(f"⚠️  Warning: Pattern not found in {file_path}")
        return False


def fix_progress_analytics_duplicates():
    """Fix duplicate methods in progress_analytics_service.py"""
    file_path = Path("app/services/progress_analytics_service.py")
    content = file_path.read_text()

    fixes_applied = 0

    # Fix 1: Remove second _get_empty_skill_analytics (line 1268)
    # Find the section around line 1268
    lines = content.split("\n")

    # Look for the second definition of _get_empty_skill_analytics
    second_def_idx = None
    first_def_idx = None
    for i, line in enumerate(lines):
        if "def _get_empty_skill_analytics(self)" in line:
            if first_def_idx is None:
                first_def_idx = i
            else:
                second_def_idx = i
                break

    if second_def_idx:
        # Find the end of the second function (next def or class keyword)
        end_idx = second_def_idx + 1
        for i in range(second_def_idx + 1, len(lines)):
            if lines[i].strip().startswith("def ") and not lines[i].strip().startswith(
                "def _get_empty_skill_analytics"
            ):
                end_idx = i
                break

        # Remove the duplicate function
        del lines[second_def_idx:end_idx]
        fixes_applied += 1
        print(
            f"✅ Fixed: {file_path} - Removed duplicate _get_empty_skill_analytics (was at line ~{second_def_idx})"
        )

    # Fix 2: Remove second _generate_skill_recommendations (line 1302)
    second_rec_idx = None
    first_rec_idx = None
    for i, line in enumerate(lines):
        if "def _generate_skill_recommendations(self" in line:
            if first_rec_idx is None:
                first_rec_idx = i
            else:
                second_rec_idx = i
                break

    if second_rec_idx:
        # Find the end of the second function
        end_idx = second_rec_idx + 1
        for i in range(second_rec_idx + 1, len(lines)):
            if lines[i].strip().startswith("def ") and not lines[i].strip().startswith(
                "def _generate_skill_recommendations"
            ):
                end_idx = i
                break

        # Remove the duplicate function
        del lines[second_rec_idx:end_idx]
        fixes_applied += 1
        print(
            f"✅ Fixed: {file_path} - Removed duplicate _generate_skill_recommendations (was at line ~{second_rec_idx})"
        )

    if fixes_applied > 0:
        file_path.write_text("\n".join(lines))
        return True
    else:
        print(f"⚠️  Warning: No duplicates found in {file_path}")
        return False


def fix_test_asyncio_import():
    """Fix duplicate asyncio import in test file"""
    file_path = Path("test_comprehensive_speech_validation.py")
    content = file_path.read_text()

    # Remove the duplicate import in main block
    old_code = """if __name__ == "__main__":
    import asyncio

    success = asyncio.run(comprehensive_speech_validation())"""

    new_code = """if __name__ == "__main__":
    # asyncio already imported at top of file
    success = asyncio.run(comprehensive_speech_validation())"""

    if old_code in content:
        content = content.replace(old_code, new_code)
        file_path.write_text(content)
        print(f"✅ Fixed: {file_path} - Removed duplicate asyncio import")
        return True
    else:
        print(f"⚠️  Warning: Pattern not found in {file_path}")
        return False


def main():
    """Run all fixes"""
    print("=" * 70)
    print("FIXING FUNCTION REDEFINITIONS (F811)")
    print("=" * 70)
    print()

    fixes = [
        ("config.py duplicates", fix_config_duplicates),
        ("ai_router.py duplicate", fix_ai_router_duplicate),
        ("progress_analytics duplicates", fix_progress_analytics_duplicates),
        ("test asyncio import", fix_test_asyncio_import),
    ]

    results = []
    for name, fix_func in fixes:
        try:
            result = fix_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ Error fixing {name}: {e}")
            results.append((name, False))
        print()

    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    total = len(results)
    successful = sum(1 for _, success in results if success)
    print(f"✅ Successfully fixed: {successful}/{total}")
    print()

    if successful < total:
        print("⚠️  Some fixes failed - manual intervention may be required")
        return 1

    print("🎉 All function redefinitions fixed!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
