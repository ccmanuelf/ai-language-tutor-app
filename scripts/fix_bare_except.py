#!/usr/bin/env python3
"""
Fix bare except clauses (E722) by analyzing context and adding appropriate exception types.
"""

from pathlib import Path
import re

# Mapping of patterns to appropriate exception types
CONTEXT_TO_EXCEPTIONS = {
    "json.loads": "(json.JSONDecodeError, TypeError, ValueError)",
    "json.dumps": "(json.JSONDecodeError, TypeError)",
    "find_transcript": "Exception",  # YouTube library exceptions
    "response.json()": "(json.JSONDecodeError, ValueError)",
    "int(": "(ValueError, TypeError)",
    "float(": "(ValueError, TypeError)",
    "decode": "(UnicodeDecodeError, AttributeError)",
    "encode": "(UnicodeEncodeError, AttributeError)",
    "open(": "(OSError, IOError)",
}


def detect_exception_type(code_block: str) -> str:
    """Detect appropriate exception type based on code context."""
    code_lower = code_block.lower()

    # Check for specific patterns
    for pattern, exception_type in CONTEXT_TO_EXCEPTIONS.items():
        if pattern.lower() in code_lower:
            return exception_type

    # Default to Exception for unknown cases
    return "Exception"


def fix_bare_except_in_file(file_path: Path) -> tuple[int, list[str]]:
    """Fix bare except clauses in a file."""
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    changes = []
    i = 0
    while i < len(lines):
        line = lines[i]

        # Check for bare except
        if re.search(r"^\s+except\s*:\s*$", line):
            indent = len(line) - len(line.lstrip())

            # Look back to find the try block
            try_start = i - 1
            while try_start >= 0 and "try:" not in lines[try_start]:
                try_start -= 1

            if try_start >= 0:
                # Get code block from try to except
                code_block = "".join(lines[try_start:i])
                exception_type = detect_exception_type(code_block)

                # Replace bare except with specific exception
                lines[i] = " " * indent + f"except {exception_type}:\n"
                changes.append(f"Line {i + 1}: except: → except {exception_type}:")

        i += 1

    if changes:
        with open(file_path, "w", encoding="utf-8") as f:
            f.writelines(lines)

    return len(changes), changes


def main():
    """Fix bare except clauses in all affected files."""
    import subprocess

    base_path = Path(__file__).parent.parent

    # Get files with E722 violations
    result = subprocess.run(
        ["flake8", "app/", "scripts/", "--select=E722", "--format=%(path)s"],
        capture_output=True,
        text=True,
        cwd=base_path,
    )

    files_to_fix = list(set(result.stdout.strip().split("\n")))
    files_to_fix = [f for f in files_to_fix if f]

    print("=" * 80)
    print("FIXING BARE EXCEPT CLAUSES (E722)")
    print("=" * 80)
    print()

    total_fixes = 0

    for file_rel in sorted(files_to_fix):
        file_path = base_path / file_rel
        if not file_path.exists():
            continue

        count, changes = fix_bare_except_in_file(file_path)
        if count > 0:
            print(f"✅ {file_rel}: {count} fixes")
            for change in changes[:3]:
                print(f"   - {change}")
            if len(changes) > 3:
                print(f"   ... and {len(changes) - 3} more")
            total_fixes += count
        else:
            print(f"✓  {file_rel}: No fixes needed")
        print()

    print("=" * 80)
    print(f"SUMMARY: Fixed {total_fixes} bare except clauses")
    print("=" * 80)


if __name__ == "__main__":
    main()
