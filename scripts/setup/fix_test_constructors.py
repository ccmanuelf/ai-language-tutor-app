#!/usr/bin/env python3
"""
Fix ConversationScenario constructors in test script
"""

import re


def fix_constructors():
    with open("scripts/test_scenario_management_system.py", "r") as f:
        content = f.read()

    # Pattern to find problematic constructor calls
    # Look for cases where there are extra commas, brackets, or missing required fields

    # First, let's identify all ConversationScenario constructor calls
    pattern = r"ConversationScenario\(\s*\n(.*?)\n\s*\)"

    def fix_constructor(match):
        constructor_body = match.group(1)
        lines = constructor_body.split("\n")

        # Clean up each line
        cleaned_lines = []
        for line in lines:
            line = line.strip()
            if line and not line.startswith(",") and not line == "],":
                cleaned_lines.append(line)

        # Ensure required fields are present
        has_vocabulary_focus = any(
            "vocabulary_focus=" in line for line in cleaned_lines
        )
        has_cultural_context = any(
            "cultural_context=" in line for line in cleaned_lines
        )
        has_learning_goals = any("learning_goals=" in line for line in cleaned_lines)

        if not has_vocabulary_focus:
            cleaned_lines.append(
                '                vocabulary_focus=["test", "vocabulary"],'
            )
        if not has_cultural_context:
            cleaned_lines.append(
                '                cultural_context={"test": "context"},'
            )
        if not has_learning_goals:
            cleaned_lines.append('                learning_goals=["test", "goals"],')

        # Remove trailing comma from last line
        if cleaned_lines and cleaned_lines[-1].endswith(","):
            cleaned_lines[-1] = cleaned_lines[-1][:-1]

        return "ConversationScenario(\n" + "\n".join(cleaned_lines) + "\n            )"

    # Apply the fix
    content = re.sub(pattern, fix_constructor, content, flags=re.DOTALL)

    # Additional cleanup for common issues
    content = re.sub(r",\s*\n\s*,", ",", content)  # Remove duplicate commas
    content = re.sub(
        r"\],\s*\n\s*\]", "]", content
    )  # Remove duplicate closing brackets
    content = re.sub(
        r"\),\s*\n\s*\)", ")", content
    )  # Remove duplicate closing parentheses

    with open("scripts/test_scenario_management_system.py", "w") as f:
        f.write(content)

    print("Fixed ConversationScenario constructors")


if __name__ == "__main__":
    fix_constructors()
