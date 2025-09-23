#!/usr/bin/env python3
"""
Full Integration Diagnostic for Task 2.2
AI Language Tutor App - Comprehensive Issue Detection

This diagnostic identifies ALL potential issues without simplification:
1. Import chain validation
2. Database dependency validation
3. API endpoint functionality
4. Frontend-backend integration
5. Missing dependencies
6. Configuration issues
7. Potential runtime errors

NO SHORTCUTS - Find every potential problem now.
"""

import sys
import os
import json
import traceback
from typing import Dict, List, Any, Optional
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


class ComprehensiveIntegrationDiagnostic:
    """Find ALL potential issues in Task 2.2 implementation"""

    def __init__(self):
        self.issues_found = []
        self.warnings = []
        self.critical_errors = []
        self.dependency_chain = []

    def run_full_diagnostic(self) -> Dict[str, Any]:
        """Run comprehensive diagnostic without shortcuts"""

        print("🔍 COMPREHENSIVE INTEGRATION DIAGNOSTIC")
        print("=" * 60)
        print("⚠️  NO SHORTCUTS - Finding ALL potential issues")
        print("=" * 60)

        start_time = datetime.now()

        # 1. Import Chain Analysis
        print("\n1️⃣ IMPORT CHAIN ANALYSIS...")
        self.analyze_import_chains()

        # 2. Database Dependencies
        print("\n2️⃣ DATABASE DEPENDENCY VALIDATION...")
        self.check_database_dependencies()

        # 3. Configuration Issues
        print("\n3️⃣ CONFIGURATION VALIDATION...")
        self.check_configuration_issues()

        # 4. API Integration Issues
        print("\n4️⃣ API INTEGRATION ANALYSIS...")
        self.check_api_integration()

        # 5. Frontend Integration Issues
        print("\n5️⃣ FRONTEND INTEGRATION ANALYSIS...")
        self.check_frontend_integration()

        # 6. Runtime Dependencies
        print("\n6️⃣ RUNTIME DEPENDENCY VALIDATION...")
        self.check_runtime_dependencies()

        # 7. Authentication Chain
        print("\n7️⃣ AUTHENTICATION CHAIN ANALYSIS...")
        self.check_authentication_chain()

        # 8. Missing Files/Components
        print("\n8️⃣ MISSING COMPONENTS ANALYSIS...")
        self.check_missing_components()

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        # Generate comprehensive report
        report = self.generate_diagnostic_report(duration)

        print(f"\n🔍 Diagnostic Completed in {duration:.2f} seconds")
        print("=" * 60)

        return report

    def analyze_import_chains(self):
        """Analyze complete import dependency chains"""

        import_chains = {
            "scenario_manager": [
                "app.services.scenario_manager",
                "app.services.scenario_manager.scenario_manager",
                "app.services.scenario_manager.ScenarioCategory",
                "app.services.scenario_manager.ScenarioDifficulty",
            ],
            "conversation_manager": [
                "app.services.conversation_manager",
                "app.services.conversation_manager.conversation_manager",
                "app.services.conversation_manager.LearningFocus",
            ],
            "api_scenarios": [
                "app.api.scenarios",
                "app.api.scenarios.router",
                "app.api.scenarios.ScenarioResponse",
            ],
        }

        for chain_name, imports in import_chains.items():
            print(f"   Checking {chain_name} import chain...")

            for import_path in imports:
                try:
                    # Attempt to import each component
                    if "." in import_path:
                        module_path, component = import_path.rsplit(".", 1)
                        module = __import__(module_path, fromlist=[component])
                        getattr(module, component)
                    else:
                        __import__(import_path)

                    print(f"     ✅ {import_path}")

                except ImportError as e:
                    error = f"Import Error in {import_path}: {str(e)}"
                    self.critical_errors.append(
                        {
                            "type": "IMPORT_ERROR",
                            "component": import_path,
                            "error": str(e),
                            "traceback": traceback.format_exc(),
                        }
                    )
                    print(f"     ❌ {import_path} - {str(e)}")

                except AttributeError as e:
                    error = f"Attribute Error in {import_path}: {str(e)}"
                    self.critical_errors.append(
                        {
                            "type": "ATTRIBUTE_ERROR",
                            "component": import_path,
                            "error": str(e),
                            "traceback": traceback.format_exc(),
                        }
                    )
                    print(f"     ❌ {import_path} - {str(e)}")

                except Exception as e:
                    error = f"Unexpected Error in {import_path}: {str(e)}"
                    self.critical_errors.append(
                        {
                            "type": "UNEXPECTED_ERROR",
                            "component": import_path,
                            "error": str(e),
                            "traceback": traceback.format_exc(),
                        }
                    )
                    print(f"     ❌ {import_path} - {str(e)}")

    def check_database_dependencies(self):
        """Check all database-related dependencies"""

        db_components = [
            "app.database.config",
            "app.models.database",
            "app.services.user_management",
        ]

        for component in db_components:
            print(f"   Checking {component}...")
            try:
                module = __import__(component, fromlist=[""])

                # Check for common database functions
                if hasattr(module, "get_db_session"):
                    print(f"     ✅ get_db_session found")
                else:
                    self.warnings.append(
                        {
                            "type": "MISSING_DB_FUNCTION",
                            "component": component,
                            "issue": "get_db_session not found",
                        }
                    )
                    print(f"     ⚠️  get_db_session not found")

                # Check for MariaDB references that should be removed
                with open(f"{component.replace('.', '/')}.py", "r") as f:
                    content = f.read()
                    if "mariadb" in content.lower():
                        self.issues_found.append(
                            {
                                "type": "DEPRECATED_REFERENCE",
                                "component": component,
                                "issue": "Contains MariaDB references - should use SQLite",
                            }
                        )
                        print(f"     ⚠️  Contains MariaDB references")

            except Exception as e:
                self.critical_errors.append(
                    {
                        "type": "DB_COMPONENT_ERROR",
                        "component": component,
                        "error": str(e),
                        "traceback": traceback.format_exc(),
                    }
                )
                print(f"     ❌ {component} - {str(e)}")

    def check_configuration_issues(self):
        """Check configuration-related issues"""

        config_files = ["app/core/config.py", "app/database/config.py", ".env.example"]

        for config_file in config_files:
            print(f"   Checking {config_file}...")

            if not os.path.exists(config_file):
                self.critical_errors.append(
                    {
                        "type": "MISSING_CONFIG_FILE",
                        "file": config_file,
                        "error": "Configuration file not found",
                    }
                )
                print(f"     ❌ File not found: {config_file}")
                continue

            try:
                with open(config_file, "r") as f:
                    content = f.read()

                # Check for exposed secrets
                secret_patterns = ["sk-", "Bearer ", "password=", "secret="]
                for pattern in secret_patterns:
                    if pattern in content:
                        self.critical_errors.append(
                            {
                                "type": "EXPOSED_SECRET",
                                "file": config_file,
                                "pattern": pattern,
                                "error": f"Potential exposed secret: {pattern}",
                            }
                        )
                        print(f"     ❌ Potential exposed secret: {pattern}")

                print(f"     ✅ {config_file} validated")

            except Exception as e:
                self.issues_found.append(
                    {"type": "CONFIG_READ_ERROR", "file": config_file, "error": str(e)}
                )
                print(f"     ❌ Error reading {config_file}: {str(e)}")

    def check_api_integration(self):
        """Check API integration issues"""

        print("   Checking API router integration...")

        try:
            # Try to import main app and check if scenarios router is included
            if os.path.exists("app/main.py"):
                with open("app/main.py", "r") as f:
                    main_content = f.read()

                if "scenarios" in main_content:
                    print("     ✅ Scenarios router referenced in main app")
                else:
                    self.critical_errors.append(
                        {
                            "type": "MISSING_ROUTER_INTEGRATION",
                            "file": "app/main.py",
                            "error": "Scenarios router not integrated in main app",
                        }
                    )
                    print("     ❌ Scenarios router not integrated in main app")

            # Check if scenarios API is importable
            from app.api.scenarios import router, get_scenarios_router

            print("     ✅ Scenarios API imports successfully")

            # Check number of routes
            routes = len(router.routes) if hasattr(router, "routes") else 0
            if routes >= 5:
                print(f"     ✅ Router has {routes} routes")
            else:
                self.warnings.append(
                    {
                        "type": "INSUFFICIENT_ROUTES",
                        "component": "scenarios_router",
                        "issue": f"Only {routes} routes found, expected 5+",
                    }
                )
                print(f"     ⚠️  Only {routes} routes found")

        except Exception as e:
            self.critical_errors.append(
                {
                    "type": "API_INTEGRATION_ERROR",
                    "error": str(e),
                    "traceback": traceback.format_exc(),
                }
            )
            print(f"     ❌ API integration error: {str(e)}")

    def check_frontend_integration(self):
        """Check frontend integration thoroughly"""

        frontend_files = [
            "app/frontend/chat.py",
            "app/frontend/styles.py",
            "app/frontend/main.py",
        ]

        required_frontend_features = {
            "app/frontend/chat.py": [
                "practice-mode-select",
                "scenario-select",
                "startConversation",
                "loadScenarios",
                "scenario-details",
            ],
            "app/frontend/styles.py": [".modal", ".scenario-info", ".vocab-tag"],
        }

        for file_path in frontend_files:
            print(f"   Checking {file_path}...")

            if not os.path.exists(file_path):
                self.critical_errors.append(
                    {
                        "type": "MISSING_FRONTEND_FILE",
                        "file": file_path,
                        "error": "Frontend file not found",
                    }
                )
                print(f"     ❌ File not found: {file_path}")
                continue

            try:
                with open(file_path, "r") as f:
                    content = f.read()

                # Check required features
                if file_path in required_frontend_features:
                    features = required_frontend_features[file_path]
                    missing_features = []

                    for feature in features:
                        if feature not in content:
                            missing_features.append(feature)

                    if missing_features:
                        self.issues_found.append(
                            {
                                "type": "MISSING_FRONTEND_FEATURES",
                                "file": file_path,
                                "missing_features": missing_features,
                            }
                        )
                        print(f"     ⚠️  Missing features: {missing_features}")
                    else:
                        print(f"     ✅ All required features present")

                # Check for JavaScript errors
                if "JavaScript" in content or "Script" in content:
                    js_issues = []
                    if "function(" in content and "async function" not in content:
                        js_issues.append("Non-async functions detected")

                    if js_issues:
                        self.warnings.append(
                            {
                                "type": "JAVASCRIPT_ISSUES",
                                "file": file_path,
                                "issues": js_issues,
                            }
                        )
                        print(f"     ⚠️  JavaScript issues: {js_issues}")

            except Exception as e:
                self.issues_found.append(
                    {"type": "FRONTEND_READ_ERROR", "file": file_path, "error": str(e)}
                )
                print(f"     ❌ Error reading {file_path}: {str(e)}")

    def check_runtime_dependencies(self):
        """Check runtime dependencies that might cause issues"""

        runtime_deps = ["fastapi", "fasthtml", "pydantic", "sqlalchemy", "asyncio"]

        for dep in runtime_deps:
            print(f"   Checking {dep}...")
            try:
                __import__(dep)
                print(f"     ✅ {dep} available")
            except ImportError:
                self.critical_errors.append(
                    {
                        "type": "MISSING_RUNTIME_DEPENDENCY",
                        "dependency": dep,
                        "error": f"Required dependency {dep} not available",
                    }
                )
                print(f"     ❌ {dep} not available")

    def check_authentication_chain(self):
        """Check authentication integration"""

        print("   Checking authentication chain...")

        auth_components = ["app.services.auth", "app.services.user_management"]

        for component in auth_components:
            try:
                module = __import__(component, fromlist=[""])
                print(f"     ✅ {component} imports")

                # Check for critical auth functions
                if component == "app.services.auth":
                    if hasattr(module, "get_current_user"):
                        print(f"     ✅ get_current_user found")
                    else:
                        self.warnings.append(
                            {
                                "type": "MISSING_AUTH_FUNCTION",
                                "component": component,
                                "function": "get_current_user",
                            }
                        )
                        print(f"     ⚠️  get_current_user not found")

            except Exception as e:
                self.critical_errors.append(
                    {
                        "type": "AUTH_CHAIN_ERROR",
                        "component": component,
                        "error": str(e),
                        "traceback": traceback.format_exc(),
                    }
                )
                print(f"     ❌ {component} - {str(e)}")

    def check_missing_components(self):
        """Check for missing components that should exist"""

        expected_files = [
            "app/services/scenario_manager.py",
            "app/api/scenarios.py",
            "app/frontend/chat.py",
            "app/frontend/styles.py",
        ]

        for file_path in expected_files:
            print(f"   Checking {file_path}...")

            if os.path.exists(file_path):
                # Check file size
                size = os.path.getsize(file_path)
                if size < 1000:  # Less than 1KB
                    self.warnings.append(
                        {
                            "type": "SMALL_FILE_SIZE",
                            "file": file_path,
                            "size": size,
                            "warning": "File may be incomplete",
                        }
                    )
                    print(f"     ⚠️  Small file size: {size} bytes")
                else:
                    print(f"     ✅ File exists ({size} bytes)")
            else:
                self.critical_errors.append(
                    {
                        "type": "MISSING_REQUIRED_FILE",
                        "file": file_path,
                        "error": "Required file not found",
                    }
                )
                print(f"     ❌ File not found: {file_path}")

    def generate_diagnostic_report(self, duration: float) -> Dict[str, Any]:
        """Generate comprehensive diagnostic report"""

        total_issues = (
            len(self.critical_errors) + len(self.issues_found) + len(self.warnings)
        )

        severity_score = (
            len(self.critical_errors) * 10
            + len(self.issues_found) * 5
            + len(self.warnings) * 1
        )

        if severity_score == 0:
            status = "EXCELLENT"
        elif severity_score <= 5:
            status = "GOOD"
        elif severity_score <= 15:
            status = "NEEDS_ATTENTION"
        elif severity_score <= 30:
            status = "PROBLEMATIC"
        else:
            status = "CRITICAL_ISSUES"

        report = {
            "diagnostic_summary": {
                "timestamp": datetime.now().isoformat(),
                "duration_seconds": round(duration, 2),
                "total_issues": total_issues,
                "critical_errors": len(self.critical_errors),
                "issues_found": len(self.issues_found),
                "warnings": len(self.warnings),
                "severity_score": severity_score,
                "status": status,
            },
            "critical_errors": self.critical_errors,
            "issues_found": self.issues_found,
            "warnings": self.warnings,
            "recommendations": self.generate_recommendations(status, severity_score),
            "next_actions": self.generate_next_actions(),
        }

        return report

    def generate_recommendations(self, status: str, severity_score: int) -> List[str]:
        """Generate specific recommendations based on findings"""

        recommendations = []

        if status == "EXCELLENT":
            recommendations.append(
                "🎉 No critical issues found - system appears robust"
            )
        elif status == "GOOD":
            recommendations.append(
                "✅ Minor issues only - address warnings when convenient"
            )
        elif status == "NEEDS_ATTENTION":
            recommendations.append("⚠️ Several issues found - address before production")
        elif status == "PROBLEMATIC":
            recommendations.append(
                "🔧 Significant issues found - fix before proceeding"
            )
        else:
            recommendations.append(
                "🚨 CRITICAL issues found - immediate attention required"
            )

        if self.critical_errors:
            recommendations.append(
                f"🔴 Fix {len(self.critical_errors)} critical error(s) immediately"
            )

        if self.issues_found:
            recommendations.append(
                f"🔧 Address {len(self.issues_found)} integration issue(s)"
            )

        if self.warnings:
            recommendations.append(f"⚠️ Review {len(self.warnings)} warning(s)")

        return recommendations

    def generate_next_actions(self) -> List[str]:
        """Generate specific next actions based on findings"""

        actions = []

        # Critical errors first
        if self.critical_errors:
            actions.append("1. IMMEDIATE: Fix all critical errors before proceeding")
            for error in self.critical_errors[:3]:  # Show first 3
                actions.append(
                    f"   - Fix {error['type']}: {error.get('component', error.get('file', 'Unknown'))}"
                )

        # High-priority issues
        if self.issues_found:
            actions.append("2. HIGH PRIORITY: Address integration issues")
            for issue in self.issues_found[:3]:  # Show first 3
                actions.append(
                    f"   - Fix {issue['type']}: {issue.get('component', issue.get('file', 'Unknown'))}"
                )

        # Warnings
        if self.warnings:
            actions.append("3. MEDIUM PRIORITY: Review warnings")

        # Always recommend testing
        actions.append("4. Run full integration test after fixes")
        actions.append("5. Test with real authentication and database")

        return actions


def main():
    """Run comprehensive diagnostic"""

    try:
        diagnostic = ComprehensiveIntegrationDiagnostic()
        report = diagnostic.run_full_diagnostic()

        # Save report
        with open("full_integration_diagnostic_report.json", "w") as f:
            json.dump(report, f, indent=2)

        # Print summary
        summary = report["diagnostic_summary"]
        print(f"\n🔍 DIAGNOSTIC SUMMARY:")
        print(f"   Status: {summary['status']}")
        print(f"   Total Issues: {summary['total_issues']}")
        print(f"   Critical Errors: {summary['critical_errors']}")
        print(f"   Issues Found: {summary['issues_found']}")
        print(f"   Warnings: {summary['warnings']}")
        print(f"   Severity Score: {summary['severity_score']}")
        print(f"   Duration: {summary['duration_seconds']}s")

        print(f"\n📋 RECOMMENDATIONS:")
        for rec in report["recommendations"]:
            print(f"   {rec}")

        print(f"\n🎯 NEXT ACTIONS:")
        for action in report["next_actions"]:
            print(f"   {action}")

        print(f"\n💾 Full report saved to: full_integration_diagnostic_report.json")

        # Return True only if no critical errors
        return summary["critical_errors"] == 0

    except Exception as e:
        print(f"❌ Diagnostic failed with error: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
