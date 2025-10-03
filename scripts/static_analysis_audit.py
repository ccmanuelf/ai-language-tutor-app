#!/usr/bin/env python3
"""
Static Analysis Audit Script - Phase 1
Task 4.2.6: Comprehensive Codebase Audit

Purpose:
    Systematically import every Python module in the codebase with all warnings
    enabled to catch any deprecation warnings not revealed by integration tests.

Approach:
    1. Discover all Python files in app/, scripts/, and test directories
    2. Import each module with DeprecationWarning set to error
    3. Capture and report any warnings or import failures
    4. Generate comprehensive audit report

Author: AI Language Tutor App Team
Date: 2025-10-02
"""

import os
import sys
import importlib
import warnings
import traceback
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import json

# Add project root to Python path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class StaticAnalysisAuditor:
    """Comprehensive static analysis audit for the codebase."""

    def __init__(self):
        self.project_root = PROJECT_ROOT
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "total_modules": 0,
            "successful_imports": 0,
            "failed_imports": 0,
            "warnings_found": 0,
            "modules_with_warnings": [],
            "import_errors": [],
            "all_modules": [],
        }

    def discover_python_files(self) -> List[Path]:
        """Discover all Python files in the project."""
        patterns = ["app/**/*.py", "scripts/*.py", "test_*.py"]

        files = []
        for pattern in patterns:
            files.extend(self.project_root.glob(pattern))

        # Filter out __pycache__ and other unwanted files
        files = [
            f
            for f in files
            if "__pycache__" not in str(f)
            and not f.name.startswith(".")
            and f.name.endswith(".py")
        ]

        return sorted(files)

    def path_to_module_name(self, file_path: Path) -> Optional[str]:
        """Convert file path to Python module name."""
        try:
            # Get relative path from project root
            rel_path = file_path.relative_to(self.project_root)

            # Convert path to module name
            parts = list(rel_path.parts)

            # Remove .py extension
            if parts[-1].endswith(".py"):
                parts[-1] = parts[-1][:-3]

            # For __init__ modules, import the package itself
            if parts[-1] == "__init__":
                # Remove __init__ and import parent package
                parts = parts[:-1]
                if len(parts) == 0:
                    return None  # Skip root __init__ if any

            module_name = ".".join(parts)
            return module_name
        except Exception as e:
            return None

    def import_module_with_warnings(
        self, module_name: str, file_path: Path
    ) -> Tuple[bool, List[str]]:
        """
        Import module with all warnings enabled.

        Returns:
            Tuple of (success: bool, warnings: List[str])
        """
        warnings_list = []

        # Custom warning handler to capture warnings
        def warning_handler(message, category, filename, lineno, file=None, line=None):
            warning_text = f"{category.__name__}: {message} (in {filename}:{lineno})"
            warnings_list.append(warning_text)

        # Save original warning settings
        original_filters = warnings.filters[:]
        original_showwarning = warnings.showwarning

        try:
            # Configure warnings
            warnings.resetwarnings()
            warnings.simplefilter("always", DeprecationWarning)
            warnings.simplefilter("always", PendingDeprecationWarning)
            warnings.simplefilter("always", FutureWarning)
            warnings.showwarning = warning_handler

            # Try to import the module
            importlib.import_module(module_name)

            return True, warnings_list

        except Exception as e:
            error_msg = f"{type(e).__name__}: {str(e)}"
            return False, [error_msg]

        finally:
            # Restore original warning settings
            warnings.filters[:] = original_filters
            warnings.showwarning = original_showwarning

    def audit_module(self, file_path: Path) -> Dict:
        """Audit a single module."""
        module_name = self.path_to_module_name(file_path)

        if module_name is None:
            return {
                "file": str(file_path.relative_to(self.project_root)),
                "module": None,
                "status": "skipped",
                "reason": "__init__ or invalid module",
            }

        success, warnings_or_errors = self.import_module_with_warnings(
            module_name, file_path
        )

        result = {
            "file": str(file_path.relative_to(self.project_root)),
            "module": module_name,
            "status": "success" if success else "failed",
        }

        if success:
            if warnings_or_errors:
                result["warnings"] = warnings_or_errors
                result["warning_count"] = len(warnings_or_errors)
            else:
                result["warning_count"] = 0
        else:
            result["errors"] = warnings_or_errors

        return result

    def run_audit(self) -> Dict:
        """Run the complete static analysis audit."""
        print("=" * 80)
        print("STATIC ANALYSIS AUDIT - Phase 1")
        print("Task 4.2.6: Comprehensive Codebase Audit")
        print("=" * 80)
        print()

        # Discover all Python files
        print("🔍 Discovering Python files...")
        python_files = self.discover_python_files()
        self.results["total_modules"] = len(python_files)
        print(f"   Found {len(python_files)} Python files")
        print()

        # Audit each module
        print("🔬 Auditing modules...")
        print()

        for i, file_path in enumerate(python_files, 1):
            rel_path = file_path.relative_to(self.project_root)
            print(f"[{i}/{len(python_files)}] {rel_path}")

            result = self.audit_module(file_path)
            self.results["all_modules"].append(result)

            if result["status"] == "success":
                self.results["successful_imports"] += 1
                warning_count = result.get("warning_count", 0)

                if warning_count > 0:
                    self.results["warnings_found"] += warning_count
                    self.results["modules_with_warnings"].append(result)
                    print(f"   ⚠️  {warning_count} warning(s) found")
                    for warning in result.get("warnings", []):
                        print(f"      - {warning}")
                else:
                    print(f"   ✅ OK")

            elif result["status"] == "failed":
                self.results["failed_imports"] += 1
                self.results["import_errors"].append(result)
                print(f"   ❌ FAILED")
                for error in result.get("errors", []):
                    print(f"      - {error}")
            else:
                print(f"   ⏭️  Skipped")

            print()

        return self.results

    def generate_summary(self) -> str:
        """Generate human-readable summary."""
        summary = []
        summary.append("=" * 80)
        summary.append("STATIC ANALYSIS AUDIT SUMMARY")
        summary.append("=" * 80)
        summary.append("")
        summary.append(f"Timestamp: {self.results['timestamp']}")
        summary.append("")
        summary.append("OVERALL RESULTS:")
        summary.append(f"  Total Modules:        {self.results['total_modules']}")
        summary.append(f"  Successful Imports:   {self.results['successful_imports']}")
        summary.append(f"  Failed Imports:       {self.results['failed_imports']}")
        summary.append(f"  Warnings Found:       {self.results['warnings_found']}")
        summary.append("")

        # Success rate
        if self.results["total_modules"] > 0:
            success_rate = (
                self.results["successful_imports"] / self.results["total_modules"]
            ) * 100
            summary.append(f"Success Rate: {success_rate:.1f}%")
            summary.append("")

        # Modules with warnings
        if self.results["modules_with_warnings"]:
            summary.append("MODULES WITH WARNINGS:")
            for module in self.results["modules_with_warnings"]:
                summary.append(
                    f"  • {module['file']} ({module['warning_count']} warnings)"
                )
                for warning in module.get("warnings", []):
                    summary.append(f"    - {warning}")
            summary.append("")

        # Failed imports
        if self.results["import_errors"]:
            summary.append("FAILED IMPORTS:")
            for module in self.results["import_errors"]:
                summary.append(f"  • {module['file']}")
                for error in module.get("errors", []):
                    summary.append(f"    - {error}")
            summary.append("")

        # Final status
        summary.append("=" * 80)
        if self.results["warnings_found"] == 0 and self.results["failed_imports"] == 0:
            summary.append("✅ AUDIT PASSED: No warnings or errors found")
        elif self.results["warnings_found"] > 0:
            summary.append(
                f"⚠️  AUDIT WARNINGS: {self.results['warnings_found']} warnings found in {len(self.results['modules_with_warnings'])} modules"
            )
        else:
            summary.append(
                f"❌ AUDIT FAILED: {self.results['failed_imports']} modules failed to import"
            )
        summary.append("=" * 80)

        return "\n".join(summary)

    def save_results(self):
        """Save audit results to files."""
        # Create validation artifacts directory
        artifacts_dir = self.project_root / "validation_artifacts" / "4.2.6"
        artifacts_dir.mkdir(parents=True, exist_ok=True)

        # Save JSON results
        json_file = artifacts_dir / "phase1_static_analysis_results.json"
        with open(json_file, "w") as f:
            json.dump(self.results, f, indent=2)
        print(f"📄 Results saved to: {json_file}")

        # Save summary report
        summary_file = artifacts_dir / "phase1_static_analysis_report.md"
        with open(summary_file, "w") as f:
            f.write("# Task 4.2.6 - Phase 1: Static Analysis Report\n\n")
            f.write(f"**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("## Objective\n\n")
            f.write(
                "Comprehensive import-time validation across entire codebase to ensure no hidden deprecation warnings exist.\n\n"
            )
            f.write("## Methodology\n\n")
            f.write(
                "1. Discovered all Python files in app/, scripts/, and test directories\n"
            )
            f.write(
                "2. Imported each module with DeprecationWarning, PendingDeprecationWarning, and FutureWarning enabled\n"
            )
            f.write("3. Captured and analyzed all warnings and import failures\n\n")
            f.write("## Results\n\n")
            f.write("```\n")
            f.write(self.generate_summary())
            f.write("\n```\n\n")

            # Detailed results
            if self.results["modules_with_warnings"]:
                f.write("## Detailed Warning Analysis\n\n")
                for module in self.results["modules_with_warnings"]:
                    f.write(f"### {module['file']}\n\n")
                    f.write(f"**Module**: `{module['module']}`\n\n")
                    f.write(f"**Warning Count**: {module['warning_count']}\n\n")
                    f.write("**Warnings**:\n")
                    for warning in module.get("warnings", []):
                        f.write(f"- {warning}\n")
                    f.write("\n")

            if self.results["import_errors"]:
                f.write("## Import Errors\n\n")
                for module in self.results["import_errors"]:
                    f.write(f"### {module['file']}\n\n")
                    f.write(f"**Module**: `{module['module']}`\n\n")
                    f.write("**Errors**:\n")
                    for error in module.get("errors", []):
                        f.write(f"- {error}\n")
                    f.write("\n")

            f.write("## Conclusion\n\n")
            if (
                self.results["warnings_found"] == 0
                and self.results["failed_imports"] == 0
            ):
                f.write(
                    "✅ **Phase 1 PASSED**: All modules imported successfully with zero warnings.\n\n"
                )
                f.write(
                    "The comprehensive deprecation elimination in Phase 0 was successful. No hidden warnings exist in the codebase.\n"
                )
            elif self.results["warnings_found"] > 0:
                f.write(
                    f"⚠️ **Phase 1 WARNINGS**: {self.results['warnings_found']} warnings found.\n\n"
                )
                f.write(
                    "Action required: Address warnings before proceeding to Phase 2.\n"
                )
            else:
                f.write(
                    f"❌ **Phase 1 FAILED**: {self.results['failed_imports']} import failures.\n\n"
                )
                f.write("Action required: Fix import errors before proceeding.\n")

        print(f"📄 Report saved to: {summary_file}")


def main():
    """Main entry point."""
    auditor = StaticAnalysisAuditor()

    try:
        # Run the audit
        results = auditor.run_audit()

        # Print summary
        print()
        print(auditor.generate_summary())
        print()

        # Save results
        auditor.save_results()

        # Exit code based on results
        if results["warnings_found"] > 0 or results["failed_imports"] > 0:
            sys.exit(1)
        else:
            sys.exit(0)

    except Exception as e:
        print(f"\n❌ Audit failed with error: {e}")
        traceback.print_exc()
        sys.exit(2)


if __name__ == "__main__":
    main()
