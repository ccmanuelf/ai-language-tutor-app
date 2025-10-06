#!/usr/bin/env python3
"""
Fix F-string without placeholders (F541) across the codebase.
Replaces f"text" with "text" when there are no placeholders.
"""

import re
from pathlib import Path


def fix_fstring_placeholders(file_path: Path) -> tuple[int, list[str]]:
    """Fix F-string placeholders in a file."""
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    changes = []
    modified = False

    for i, line in enumerate(lines):
        original_line = line

        # Pattern 1: f"text without placeholders" -> "text without placeholders"
        # Only match if no { } brackets present
        # Match both single and double quotes
        pattern1 = r'f"([^"{]*)"'
        pattern2 = r"f'([^'{]*)'"

        # Check if line has f-string without placeholders
        if re.search(pattern1, line):
            # Ensure no { } in the string
            matches = re.findall(r'f"([^"]*)"', line)
            for match in matches:
                if "{" not in match and "}" not in match:
                    line = line.replace(f'f"{match}"', f'"{match}"')
                    modified = True
                    changes.append(f'Line {i + 1}: f"{match}" → "{match}"')

        if re.search(pattern2, line):
            # Ensure no { } in the string
            matches = re.findall(r"f'([^']*)'", line)
            for match in matches:
                if "{" not in match and "}" not in match:
                    line = line.replace(f"f'{match}'", f"'{match}'")
                    modified = True
                    changes.append(f"Line {i + 1}: f'{match}' → '{match}'")

        lines[i] = line

    if modified:
        with open(file_path, "w", encoding="utf-8") as f:
            f.writelines(lines)

    return len(changes), changes


def main():
    """Fix F-string placeholders in all Python files."""
    base_path = Path(__file__).parent.parent

    # Get all affected files from flake8
    import subprocess

    result = subprocess.run(
        ["flake8", "app/", "scripts/", "--select=F541", "--format=%(path)s"],
        capture_output=True,
        text=True,
        cwd=base_path,
    )

    files_to_fix = list(set(result.stdout.strip().split("\n")))
    files_to_fix = [f for f in files_to_fix if f]  # Remove empty strings

    print("=" * 80)
    print("FIXING F-STRING PLACEHOLDERS (F541)")
    print("=" * 80)
    print()

    total_fixes = 0

    for file_rel in sorted(files_to_fix):
        file_path = base_path / file_rel
        if not file_path.exists():
            continue

        count, changes = fix_fstring_placeholders(file_path)
        if count > 0:
            print(f"✅ {file_rel}: {count} fixes")
            for change in changes[:2]:  # Show first 2 changes
                print(f"   - {change}")
            if len(changes) > 2:
                print(f"   ... and {len(changes) - 2} more")
            total_fixes += count
        else:
            print(f"✓  {file_rel}: No fixes needed")
        print()

    print("=" * 80)
    print(f"SUMMARY: Fixed {total_fixes} F-string placeholder issues")
    print("=" * 80)


if __name__ == "__main__":
    main()
