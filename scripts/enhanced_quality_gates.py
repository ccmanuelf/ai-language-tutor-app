#!/usr/bin/env python3
"""
Enhanced Quality Gates Validation System with Production Reality Checks
Implements prevention measures from Task 3.1.8 root cause analysis

New Gates Added:
- Gate 6: Production Reality Check
- Gate 7: Schema Integrity Validation
- Gate 8: Error Handling Verification
"""

import json
import os
import sqlite3
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any


class EnhancedQualityGatesValidator:
    """Enhanced quality gates with production reality checks"""

    def __init__(self, task_id: str):
        self.task_id = task_id
        self.validation_results = {}
        self.production_db_path = "data/ai_language_tutor.db"
        self.artifacts_path = f"validation_artifacts/{task_id}"

    def gate_1_evidence_collection(self) -> Dict[str, Any]:
        """Enhanced Gate 1: Evidence Collection + Schema Validation"""
        print("🚨 ENHANCED GATE 1: EVIDENCE COLLECTION + SCHEMA")
        print("=" * 50)

        result = {
            "gate_name": "Enhanced Evidence Collection",
            "status": "CHECKING",
            "checks": {},
            "details": [],
        }

        # Original evidence collection
        if not os.path.exists(self.artifacts_path):
            result["status"] = "FAILED"
            result["details"].append("❌ Artifacts directory missing")
            return result

        files = list(Path(self.artifacts_path).glob("*"))
        large_files = [f for f in files if f.stat().st_size > 1024]

        result["checks"]["artifacts_directory_exists"] = True
        result["checks"]["total_files"] = len(files)
        result["checks"]["large_files_count"] = len(large_files)
        result["checks"]["original_evidence_sufficient"] = len(large_files) >= 3

        # NEW: Schema validation
        if os.path.exists(self.production_db_path):
            result["checks"]["production_db_exists"] = True

            # Check if test results mention production database
            test_files = [f for f in files if "test" in f.name.lower()]
            production_testing = False

            for test_file in test_files:
                try:
                    content = test_file.read_text()
                    if (
                        "data/ai_language_tutor.db" in content
                        and "production" in content.lower()
                    ):
                        production_testing = True
                        break
                except:
                    pass

            result["checks"]["production_database_testing"] = production_testing
        else:
            result["checks"]["production_db_exists"] = False
            result["checks"]["production_database_testing"] = False

        # Determine overall status
        critical_checks = [
            result["checks"]["original_evidence_sufficient"],
            result["checks"]["production_db_exists"],
            result["checks"]["production_database_testing"],
        ]

        if all(critical_checks):
            result["status"] = "PASSED"
            result["details"].append("✅ Enhanced evidence collection passed")
        else:
            result["status"] = "FAILED"
            result["details"].append("❌ Enhanced evidence collection failed")

        return result

    def gate_6_production_reality_check(self) -> Dict[str, Any]:
        """NEW Gate 6: Production Reality Check"""
        print("🚨 GATE 6: PRODUCTION REALITY CHECK")
        print("=" * 40)

        result = {
            "gate_name": "Production Reality Check",
            "status": "CHECKING",
            "checks": {},
            "details": [],
        }

        # Check if production database was actually used in testing
        test_files = list(Path(self.artifacts_path).glob("*test*"))
        production_usage = False
        temp_db_usage = False

        for test_file in test_files:
            try:
                content = test_file.read_text()
                if "data/ai_language_tutor.db" in content:
                    production_usage = True
                if "tmp" in content.lower() or "temp" in content.lower():
                    temp_db_usage = True
            except:
                pass

        # Check for production-realistic test files specifically
        production_test_files = [
            f
            for f in test_files
            if "production" in f.name.lower() or "realistic" in f.name.lower()
        ]
        has_production_tests = len(production_test_files) > 0

        result["checks"]["production_database_used"] = production_usage
        result["checks"]["has_production_tests"] = has_production_tests
        result["checks"]["no_temporary_database_usage"] = (
            not temp_db_usage or has_production_tests
        )

        # Verify actual database connectivity during testing
        if os.path.exists(self.production_db_path):
            try:
                conn = sqlite3.connect(self.production_db_path)
                cursor = conn.cursor()

                # Check for task-specific tables (if applicable)
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]

                task_tables = 0
                if "conversation_metrics" in tables:
                    task_tables += 1
                if "skill_progress_metrics" in tables:
                    task_tables += 1
                if "learning_path_recommendations" in tables:
                    task_tables += 1
                if "memory_retention_analysis" in tables:
                    task_tables += 1

                result["checks"]["task_tables_exist"] = task_tables >= 4
                result["checks"]["database_accessible"] = True

                conn.close()
            except Exception as e:
                result["checks"]["database_accessible"] = False
                result["details"].append(f"❌ Database access error: {str(e)}")
        else:
            result["checks"]["database_accessible"] = False
            result["checks"]["task_tables_exist"] = False

        # Overall status
        critical_checks = [
            result["checks"]["production_database_used"],
            result["checks"]["no_temporary_database_usage"],
            result["checks"]["database_accessible"],
        ]

        if all(critical_checks):
            result["status"] = "PASSED"
            result["details"].append("✅ Production reality check passed")
        else:
            result["status"] = "FAILED"
            result["details"].append("❌ Production reality check failed")

        return result

    def gate_7_schema_integrity_validation(self) -> Dict[str, Any]:
        """NEW Gate 7: Schema Integrity Validation"""
        print("🚨 GATE 7: SCHEMA INTEGRITY VALIDATION")
        print("=" * 45)

        result = {
            "gate_name": "Schema Integrity Validation",
            "status": "CHECKING",
            "checks": {},
            "details": [],
        }

        if not os.path.exists(self.production_db_path):
            result["status"] = "FAILED"
            result["details"].append("❌ Production database not found")
            return result

        try:
            conn = sqlite3.connect(self.production_db_path)
            cursor = conn.cursor()

            # Check essential tables exist
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]

            essential_tables = [
                "conversation_metrics",
                "skill_progress_metrics",
                "learning_path_recommendations",
                "memory_retention_analysis",
                "admin_spaced_repetition_config",
            ]

            existing_essential = [
                table for table in essential_tables if table in tables
            ]
            result["checks"]["essential_tables_exist"] = len(existing_essential)
            result["checks"]["all_essential_tables"] = len(existing_essential) == len(
                essential_tables
            )

            # Check for data consistency
            data_checks = {}
            for table in existing_essential:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    data_checks[table] = count
                except Exception as e:
                    data_checks[table] = f"ERROR: {str(e)}"

            result["checks"]["table_data_status"] = data_checks
            result["checks"]["no_table_errors"] = all(
                isinstance(v, int) for v in data_checks.values()
            )

            conn.close()

            # Overall status
            if (
                result["checks"]["all_essential_tables"]
                and result["checks"]["no_table_errors"]
            ):
                result["status"] = "PASSED"
                result["details"].append("✅ Schema integrity validation passed")
            else:
                result["status"] = "FAILED"
                result["details"].append("❌ Schema integrity validation failed")

        except Exception as e:
            result["status"] = "FAILED"
            result["details"].append(f"❌ Schema validation error: {str(e)}")

        return result

    def gate_8_error_handling_verification(self) -> Dict[str, Any]:
        """NEW Gate 8: Error Handling Verification"""
        print("🚨 GATE 8: ERROR HANDLING VERIFICATION")
        print("=" * 42)

        result = {
            "gate_name": "Error Handling Verification",
            "status": "CHECKING",
            "checks": {},
            "details": [],
        }

        # Check test files for error handling validation
        test_files = list(Path(self.artifacts_path).glob("*test*"))
        error_handling_evidence = {
            "empty_data_tests": False,
            "error_recovery_tests": False,
            "graceful_degradation": False,
            "safe_statistics": False,
        }

        for test_file in test_files:
            try:
                content = test_file.read_text()
                content_lower = content.lower()

                if "empty data" in content_lower or "empty_data" in content_lower:
                    error_handling_evidence["empty_data_tests"] = True
                if (
                    "error recovery" in content_lower
                    or "error_recovery" in content_lower
                ):
                    error_handling_evidence["error_recovery_tests"] = True
                if "graceful" in content_lower or "degradation" in content_lower:
                    error_handling_evidence["graceful_degradation"] = True
                if "safe_mean" in content or "statistics.mean" not in content:
                    error_handling_evidence["safe_statistics"] = True

            except:
                pass

        result["checks"] = error_handling_evidence

        # Check source code for safe_mean usage
        source_files = list(Path("app").glob("**/*.py"))
        unsafe_statistics_usage = 0
        safe_mean_implementations = 0

        for source_file in source_files:
            try:
                content = source_file.read_text()
                # Only count statistics.mean() that are NOT inside safe_mean function definitions
                lines = content.split("\n")
                in_safe_mean_function = False

                for line in lines:
                    stripped_line = line.strip()
                    if "def safe_mean(" in stripped_line:
                        in_safe_mean_function = True
                    elif stripped_line.startswith("def ") and in_safe_mean_function:
                        in_safe_mean_function = False
                    elif "statistics.mean(" in line and not in_safe_mean_function:
                        unsafe_statistics_usage += 1
                if "safe_mean(" in content or "def safe_mean" in content:
                    safe_mean_implementations += 1
            except:
                pass

        result["checks"]["unsafe_statistics_usage"] = unsafe_statistics_usage
        result["checks"]["safe_mean_implementations"] = safe_mean_implementations
        result["checks"]["statistics_handling_safe"] = (
            unsafe_statistics_usage == 0 and safe_mean_implementations > 0
        )

        # Overall status
        critical_checks = [
            error_handling_evidence["empty_data_tests"],
            error_handling_evidence["error_recovery_tests"],
            result["checks"]["statistics_handling_safe"],
        ]

        if all(critical_checks):
            result["status"] = "PASSED"
            result["details"].append("✅ Error handling verification passed")
        else:
            result["status"] = "FAILED"
            result["details"].append("❌ Error handling verification failed")

        return result

    def run_enhanced_validation(self) -> Dict[str, Any]:
        """Run all enhanced quality gates"""
        print("🔒 ENHANCED QUALITY GATES VALIDATION SYSTEM")
        print("=" * 55)
        print(f"Task ID: {self.task_id}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print()

        gates = [
            self.gate_1_evidence_collection,
            self.gate_6_production_reality_check,
            self.gate_7_schema_integrity_validation,
            self.gate_8_error_handling_verification,
        ]

        results = {}
        passed_gates = 0
        total_gates = len(gates)

        for gate_func in gates:
            try:
                gate_result = gate_func()
                results[gate_result["gate_name"]] = gate_result

                if gate_result["status"] == "PASSED":
                    passed_gates += 1
                    print(f"✅ {gate_result['gate_name']}: PASSED")
                else:
                    print(f"❌ {gate_result['gate_name']}: FAILED")

                for detail in gate_result["details"]:
                    print(f"   {detail}")
                print()

            except Exception as e:
                print(f"❌ CRITICAL ERROR in {gate_func.__name__}: {str(e)}")
                results[gate_func.__name__] = {
                    "gate_name": gate_func.__name__,
                    "status": "ERROR",
                    "error": str(e),
                }

        # Summary
        print("=" * 55)
        print("🎯 ENHANCED QUALITY GATES SUMMARY")
        print("=" * 55)

        for gate_name, gate_result in results.items():
            status = gate_result["status"]
            status_emoji = "✅" if status == "PASSED" else "❌"
            print(f"{status_emoji} {gate_name}: {status}")

        print(f"\nOverall: {passed_gates}/{total_gates} gates passed")

        if passed_gates == total_gates:
            print("\n🎉 ALL ENHANCED QUALITY GATES PASSED")
            print("🎉 Task meets production readiness standards")
            overall_status = "ALL_PASSED"
        else:
            print("\n⚠️  ENHANCED QUALITY GATES FAILED")
            print("⚠️  Task does not meet production standards")
            overall_status = "FAILED"

        # Save results
        final_results = {
            "task_id": self.task_id,
            "timestamp": datetime.now().isoformat(),
            "validation_type": "Enhanced Quality Gates",
            "gates_passed": passed_gates,
            "gates_total": total_gates,
            "overall_status": overall_status,
            "gate_results": results,
        }

        os.makedirs("validation_results", exist_ok=True)
        results_file = f"validation_results/enhanced_quality_gates_{self.task_id}.json"

        with open(results_file, "w") as f:
            json.dump(final_results, f, indent=2)

        print(f"\n📁 Results saved: {results_file}")

        return final_results


def main():
    """Main entry point"""
    if len(sys.argv) != 2:
        print("Usage: python enhanced_quality_gates.py <task_id>")
        print("Example: python enhanced_quality_gates.py 3.1.8")
        sys.exit(1)

    task_id = sys.argv[1]
    validator = EnhancedQualityGatesValidator(task_id)
    results = validator.run_enhanced_validation()

    # Return appropriate exit code
    if results["overall_status"] == "ALL_PASSED":
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
