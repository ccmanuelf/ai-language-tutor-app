#!/usr/bin/env python3
"""
Fix boolean comparison issues (E712) across the codebase.
Replaces:
  - == True with is True (or direct evaluation in if statements)
  - == False with is False (or not in if statements)
"""

import re
from pathlib import Path


def fix_boolean_comparisons(file_path: Path) -> tuple[int, list[str]]:
    """Fix boolean comparisons in a file."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    original_content = content
    changes = []

    # Pattern 1: assert ... == True -> assert ...
    pattern1 = r"assert\s+(.+?)\s+==\s+True(?=,|\s*$)"
    matches1 = re.findall(pattern1, content)
    if matches1:
        content = re.sub(pattern1, r"assert \1", content)
        changes.extend([f"assert {m} == True → assert {m}" for m in matches1])

    # Pattern 2: assert ... == False -> assert not ...
    pattern2 = r"assert\s+(.+?)\s+==\s+False(?=,|\s*$)"
    matches2 = re.findall(pattern2, content)
    if matches2:
        content = re.sub(pattern2, r"assert not \1", content)
        changes.extend([f"assert {m} == False → assert not {m}" for m in matches2])

    # Pattern 3: filter(...== True) -> filter(...is True)
    pattern3 = r"(\w+)\s+==\s+True\)"
    matches3 = re.findall(pattern3, content)
    if matches3:
        content = re.sub(pattern3, r"\1 is True)", content)
        changes.extend([f"{m} == True → {m} is True (in filter)" for m in matches3])

    # Pattern 4: .field == True in filters -> .field is True
    pattern4 = r"\.(\w+)\s+==\s+True(?=,|\))"
    matches4 = re.findall(pattern4, content)
    if matches4:
        content = re.sub(pattern4, r".\1 is True", content)
        changes.extend([f".{m} == True → .{m} is True" for m in matches4])

    # Pattern 5: .is_enabled == False -> .is_enabled is False
    pattern5 = r"\.(\w+)\s+==\s+False(?=,|\))"
    matches5 = re.findall(pattern5, content)
    if matches5:
        content = re.sub(pattern5, r".\1 is False", content)
        changes.extend([f".{m} == False → .{m} is False" for m in matches5])

    if content != original_content:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return len(changes), changes

    return 0, []


def main():
    """Fix boolean comparisons in all affected files."""
    files_to_fix = [
        "app/api/admin.py",
        "app/api/auth.py",
        "app/services/ai_test_suite.py",
        "app/services/user_management.py",
        "scripts/test_feature_toggle_system.py",
        "scripts/validate_feature_toggles.py",
    ]

    base_path = Path(__file__).parent.parent
    total_fixes = 0

    print("=" * 80)
    print("FIXING BOOLEAN COMPARISONS (E712)")
    print("=" * 80)
    print()

    for file_rel in files_to_fix:
        file_path = base_path / file_rel
        if not file_path.exists():
            print(f"⚠️  {file_rel}: File not found")
            continue

        count, changes = fix_boolean_comparisons(file_path)
        if count > 0:
            print(f"✅ {file_rel}: {count} fixes")
            for change in changes[:3]:  # Show first 3 changes
                print(f"   - {change}")
            if len(changes) > 3:
                print(f"   ... and {len(changes) - 3} more")
            total_fixes += count
        else:
            print(f"✓  {file_rel}: No issues found")
        print()

    print("=" * 80)
    print(f"SUMMARY: Fixed {total_fixes} boolean comparison issues")
    print("=" * 80)


if __name__ == "__main__":
    main()
