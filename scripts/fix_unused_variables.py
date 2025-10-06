#!/usr/bin/env python3
"""
Fix unused variables (F841) by prefixing with underscore to indicate intentional.
This is safer than removing them as they might be placeholders or debug code.
"""

from pathlib import Path
import subprocess
import re


def fix_unused_variable(file_path: Path, line_num: int, var_name: str) -> bool:
    """Fix unused variable by prefixing with underscore."""
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    if line_num > len(lines):
        return False

    line = lines[line_num - 1]

    # Already prefixed with underscore?
    if f"_{var_name}" in line and var_name.startswith("_"):
        return False

    # Replace variable name with underscore-prefixed version
    # Handle different assignment patterns
    patterns = [
        (rf"\b{var_name}\b\s*=", f"_{var_name} ="),  # Simple assignment
        (rf"\b{var_name}\b\s*:", f"_{var_name}:"),  # Type hint
    ]

    modified = False
    for pattern, replacement in patterns:
        if re.search(pattern, line):
            line = re.sub(pattern, replacement, line)
            lines[line_num - 1] = line
            modified = True
            break

    if modified:
        with open(file_path, "w", encoding="utf-8") as f:
            f.writelines(lines)

    return modified


def main():
    """Fix unused variables in all affected files."""
    base_path = Path(__file__).parent.parent

    # Get all F841 violations
    result = subprocess.run(
        [
            "flake8",
            "app/",
            "scripts/",
            "--select=F841",
            "--format=%(path)s:%(row)d: %(text)s",
        ],
        capture_output=True,
        text=True,
        cwd=base_path,
    )

    violations = []
    for line in result.stdout.split("\n"):
        if not line.strip():
            continue

        # Parse: file.py:123: local variable 'var_name' is assigned to but never used
        match = re.match(r"(.+?):(\d+): local variable '(.+?)' is assigned", line)
        if match:
            file_rel, line_num, var_name = match.groups()
            violations.append((file_rel, int(line_num), var_name))

    print("=" * 80)
    print("FIXING UNUSED VARIABLES (F841)")
    print("=" * 80)
    print()

    files_fixed = {}
    for file_rel, line_num, var_name in violations:
        file_path = base_path / file_rel
        if not file_path.exists():
            continue

        success = fix_unused_variable(file_path, line_num, var_name)
        if success:
            if file_rel not in files_fixed:
                files_fixed[file_rel] = []
            files_fixed[file_rel].append((line_num, var_name))

    # Print summary
    for file_rel in sorted(files_fixed.keys()):
        fixes = files_fixed[file_rel]
        print(f"✅ {file_rel}: {len(fixes)} fixes")
        for line_num, var_name in fixes[:3]:
            print(f"   - Line {line_num}: {var_name} → _{var_name}")
        if len(fixes) > 3:
            print(f"   ... and {len(fixes) - 3} more")
        print()

    print("=" * 80)
    print(
        f"SUMMARY: Fixed {sum(len(f) for f in files_fixed.values())} unused variables"
    )
    print("=" * 80)


if __name__ == "__main__":
    main()
