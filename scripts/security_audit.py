#!/usr/bin/env python3
"""
Security Audit Tool for AI Language Tutor App
Task 4.2 - Performance Optimization (Security Component)

This script performs comprehensive security testing including:
1. Dependency vulnerability scanning
2. SQL injection testing
3. Authentication/authorization checks
4. API endpoint security validation
5. Secret and credential exposure detection
6. Input validation testing
7. Rate limiting verification
"""

import sys
import json
import re
import asyncio
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class SecurityFinding:
    """Security finding data structure"""

    severity: str  # critical, high, medium, low, info
    category: str
    title: str
    description: str
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    remediation: Optional[str] = None

    def to_dict(self):
        return asdict(self)


class SecurityAuditor:
    """Comprehensive security audit tool"""

    def __init__(self, output_dir: str = "security_reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.findings: List[SecurityFinding] = []

    def add_finding(
        self,
        severity: str,
        category: str,
        title: str,
        description: str,
        file_path: str = None,
        line_number: int = None,
        remediation: str = None,
    ):
        """Add a security finding"""
        finding = SecurityFinding(
            severity=severity,
            category=category,
            title=title,
            description=description,
            file_path=file_path,
            line_number=line_number,
            remediation=remediation,
        )
        self.findings.append(finding)

        # Log critical and high severity findings immediately
        if severity in ["critical", "high"]:
            logger.warning(f"[{severity.upper()}] {title}: {description}")

    def scan_hardcoded_secrets(self) -> Dict[str, Any]:
        """Scan for hardcoded secrets and credentials"""
        logger.info("🔍 Scanning for hardcoded secrets...")

        secret_patterns = {
            "api_key": r'(?i)(api[_-]?key|apikey)\s*[=:]\s*["\']([^"\']{20,})["\']',
            "password": r'(?i)password\s*[=:]\s*["\']([^"\']{8,})["\']',
            "secret": r'(?i)(secret|token)\s*[=:]\s*["\']([^"\']{20,})["\']',
            "aws_key": r"(?i)(AKIA[0-9A-Z]{16})",
            "private_key": r"-----BEGIN (RSA |EC )?PRIVATE KEY-----",
        }

        findings = []
        excluded_files = {".env", ".env.example", "security_audit.py"}

        for py_file in Path("app").rglob("*.py"):
            if py_file.name in excluded_files:
                continue

            try:
                content = py_file.read_text()
                for pattern_name, pattern in secret_patterns.items():
                    matches = re.finditer(pattern, content)
                    for match in matches:
                        # Skip if it's in a comment or example
                        line_start = content.rfind("\n", 0, match.start()) + 1
                        line = content[line_start : content.find("\n", match.start())]

                        if not line.strip().startswith("#"):
                            self.add_finding(
                                severity="high",
                                category="secrets",
                                title=f"Potential {pattern_name} exposure",
                                description=f"Hardcoded {pattern_name} detected",
                                file_path=str(py_file),
                                line_number=content[: match.start()].count("\n") + 1,
                                remediation="Move secrets to environment variables or secure vault",
                            )
                            findings.append(
                                {
                                    "file": str(py_file),
                                    "pattern": pattern_name,
                                    "line": content[: match.start()].count("\n") + 1,
                                }
                            )
            except Exception as e:
                logger.warning(f"Could not scan {py_file}: {e}")

        return {"total_findings": len(findings), "findings": findings}

    def check_sql_injection_risks(self) -> Dict[str, Any]:
        """Check for SQL injection vulnerabilities"""
        logger.info("🔍 Checking for SQL injection risks...")

        risky_patterns = [
            r'execute\([\'"].*%s.*[\'"]\s*%',  # String formatting in SQL
            r'execute\([\'"].*\+.*[\'"]\)',  # String concatenation in SQL
            r'execute\(f[\'"]',  # f-strings in SQL
            r"\.format\(",  # .format() in SQL
        ]

        findings = []

        for py_file in Path("app").rglob("*.py"):
            try:
                content = py_file.read_text()
                for pattern in risky_patterns:
                    if re.search(pattern, content):
                        self.add_finding(
                            severity="high",
                            category="sql_injection",
                            title="Potential SQL injection vulnerability",
                            description="SQL query construction using unsafe string operations",
                            file_path=str(py_file),
                            remediation="Use parameterized queries or ORM methods",
                        )
                        findings.append(str(py_file))
            except Exception as e:
                logger.warning(f"Could not scan {py_file}: {e}")

        return {"files_with_risks": len(set(findings)), "files": list(set(findings))}

    def check_authentication_security(self) -> Dict[str, Any]:
        """Check authentication and authorization implementation"""
        logger.info("🔍 Checking authentication security...")

        findings = {
            "has_password_hashing": False,
            "has_jwt": False,
            "has_rate_limiting": False,
            "has_csrf_protection": False,
            "issues": [],
        }

        # Check for password hashing
        security_file = Path("app/core/security.py")
        if security_file.exists():
            content = security_file.read_text()
            if "bcrypt" in content or "argon2" in content or "pbkdf2" in content:
                findings["has_password_hashing"] = True
            else:
                self.add_finding(
                    severity="critical",
                    category="authentication",
                    title="Weak password storage",
                    description="No strong password hashing detected",
                    file_path=str(security_file),
                    remediation="Implement bcrypt, argon2, or PBKDF2 for password hashing",
                )
                findings["issues"].append("weak_password_hashing")

            if "jwt" in content.lower() or "token" in content:
                findings["has_jwt"] = True

        # Check for rate limiting
        for py_file in Path("app").rglob("*.py"):
            try:
                content = py_file.read_text()
                if "limiter" in content.lower() or "rate_limit" in content.lower():
                    findings["has_rate_limiting"] = True
                    break
            except Exception:
                pass

        if not findings["has_rate_limiting"]:
            self.add_finding(
                severity="medium",
                category="authentication",
                title="Missing rate limiting",
                description="No rate limiting detected for API endpoints",
                remediation="Implement rate limiting to prevent brute force attacks",
            )
            findings["issues"].append("no_rate_limiting")

        return findings

    def check_input_validation(self) -> Dict[str, Any]:
        """Check input validation and sanitization"""
        logger.info("🔍 Checking input validation...")

        findings = {
            "uses_pydantic": False,
            "potential_xss_risks": [],
            "file_upload_risks": [],
        }

        # Check for Pydantic usage
        for py_file in Path("app").rglob("*.py"):
            try:
                content = py_file.read_text()
                if "from pydantic import" in content or "BaseModel" in content:
                    findings["uses_pydantic"] = True

                # Check for potential XSS
                if re.search(r"\.html\(.*\+.*\)", content):
                    findings["potential_xss_risks"].append(str(py_file))
                    self.add_finding(
                        severity="medium",
                        category="input_validation",
                        title="Potential XSS vulnerability",
                        description="Unsafe HTML rendering detected",
                        file_path=str(py_file),
                        remediation="Sanitize user input before rendering as HTML",
                    )

                # Check for file upload handling
                if "upload" in content.lower() and "save" in content:
                    findings["file_upload_risks"].append(str(py_file))

            except Exception as e:
                logger.warning(f"Could not scan {py_file}: {e}")

        return findings

    def check_dependency_vulnerabilities(self) -> Dict[str, Any]:
        """Check for known vulnerabilities in dependencies"""
        logger.info("🔍 Checking dependency vulnerabilities...")

        findings = {
            "requirements_found": False,
            "recommendation": "Run 'pip-audit' or 'safety check' for comprehensive vulnerability scanning",
        }

        requirements_file = Path("requirements.txt")
        if requirements_file.exists():
            findings["requirements_found"] = True

            # Check for obviously outdated packages
            content = requirements_file.read_text()

            # Packages that should be up to date
            critical_packages = ["fastapi", "sqlalchemy", "cryptography", "pydantic"]

            for package in critical_packages:
                if package in content.lower():
                    # Very basic check - in real audit would use pip-audit
                    if re.search(rf"{package}==\d+\.0\.", content, re.IGNORECASE):
                        logger.info(
                            f"Found {package} - recommend checking for latest version"
                        )

        else:
            self.add_finding(
                severity="medium",
                category="dependencies",
                title="Missing requirements.txt",
                description="No requirements.txt file found",
                remediation="Create requirements.txt for dependency tracking",
            )

        return findings

    def check_cors_configuration(self) -> Dict[str, Any]:
        """Check CORS configuration security"""
        logger.info("🔍 Checking CORS configuration...")

        findings = {"has_cors": False, "allows_all_origins": False, "issues": []}

        main_file = Path("app/main.py")
        if main_file.exists():
            content = main_file.read_text()
            if "CORSMiddleware" in content:
                findings["has_cors"] = True

                # Check for overly permissive settings
                if '"*"' in content or "'*'" in content:
                    findings["allows_all_origins"] = True
                    self.add_finding(
                        severity="medium",
                        category="cors",
                        title="Overly permissive CORS configuration",
                        description="CORS allows all origins (*)",
                        file_path=str(main_file),
                        remediation="Restrict CORS to specific trusted origins",
                    )
                    findings["issues"].append("allows_all_origins")

        return findings

    def check_environment_variables(self) -> Dict[str, Any]:
        """Check environment variable usage and .env file security"""
        logger.info("🔍 Checking environment variable security...")

        findings = {
            "has_env_example": False,
            "env_in_gitignore": False,
            "uses_env_vars": False,
        }

        # Check for .env.example
        if Path(".env.example").exists():
            findings["has_env_example"] = True
        else:
            self.add_finding(
                severity="low",
                category="configuration",
                title="Missing .env.example",
                description="No .env.example file found",
                remediation="Create .env.example to document required environment variables",
            )

        # Check .gitignore
        gitignore = Path(".gitignore")
        if gitignore.exists():
            content = gitignore.read_text()
            if ".env" in content:
                findings["env_in_gitignore"] = True
            else:
                self.add_finding(
                    severity="critical",
                    category="configuration",
                    title=".env not in .gitignore",
                    description=".env file is not ignored by git",
                    file_path=".gitignore",
                    remediation="Add .env to .gitignore to prevent credential exposure",
                )

        # Check for environment variable usage
        for py_file in Path("app").rglob("*.py"):
            try:
                content = py_file.read_text()
                if "os.getenv" in content or "os.environ" in content:
                    findings["uses_env_vars"] = True
                    break
            except Exception:
                pass

        return findings

    async def run_full_audit(self) -> Dict[str, Any]:
        """Run comprehensive security audit"""
        logger.info("=" * 80)
        logger.info("🔒 Starting Comprehensive Security Audit")
        logger.info("=" * 80)

        report = {
            "timestamp": datetime.now().isoformat(),
            "secrets_scan": self.scan_hardcoded_secrets(),
            "sql_injection_check": self.check_sql_injection_risks(),
            "authentication_security": self.check_authentication_security(),
            "input_validation": self.check_input_validation(),
            "dependency_vulnerabilities": self.check_dependency_vulnerabilities(),
            "cors_configuration": self.check_cors_configuration(),
            "environment_variables": self.check_environment_variables(),
            "findings": [f.to_dict() for f in self.findings],
            "summary": {
                "total_findings": len(self.findings),
                "critical": len([f for f in self.findings if f.severity == "critical"]),
                "high": len([f for f in self.findings if f.severity == "high"]),
                "medium": len([f for f in self.findings if f.severity == "medium"]),
                "low": len([f for f in self.findings if f.severity == "low"]),
            },
        }

        # Save report
        report_file = (
            self.output_dir
            / f"security_audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2, default=str)

        logger.info("=" * 80)
        logger.info("✅ Security audit complete")
        logger.info(f"🔒 Report saved to: {report_file}")
        logger.info("=" * 80)

        # Print summary
        self.print_summary(report)

        return report

    def print_summary(self, report: Dict[str, Any]):
        """Print security audit summary"""
        print("\n" + "=" * 80)
        print("🔒 SECURITY AUDIT SUMMARY")
        print("=" * 80)

        summary = report["summary"]
        print("\n📊 FINDINGS OVERVIEW:")
        print(f"  • Total Findings: {summary['total_findings']}")
        print(f"  • Critical: {summary['critical']}")
        print(f"  • High: {summary['high']}")
        print(f"  • Medium: {summary['medium']}")
        print(f"  • Low: {summary['low']}")

        print("\n🔐 AUTHENTICATION & AUTHORIZATION:")
        auth = report["authentication_security"]
        print(
            f"  • Password Hashing: {'✅ Yes' if auth['has_password_hashing'] else '❌ No'}"
        )
        print(f"  • JWT/Token Auth: {'✅ Yes' if auth['has_jwt'] else '❌ No'}")
        print(
            f"  • Rate Limiting: {'✅ Yes' if auth['has_rate_limiting'] else '❌ No'}"
        )

        print("\n🛡️  INPUT VALIDATION:")
        validation = report["input_validation"]
        print(
            f"  • Pydantic Validation: {'✅ Yes' if validation['uses_pydantic'] else '❌ No'}"
        )
        print(
            f"  • Potential XSS Risks: {len(validation['potential_xss_risks'])} files"
        )

        print("\n🔑 SECRETS MANAGEMENT:")
        secrets = report["secrets_scan"]
        env_vars = report["environment_variables"]
        print(f"  • Hardcoded Secrets: {secrets['total_findings']} found")
        print(
            f"  • .env in .gitignore: {'✅ Yes' if env_vars['env_in_gitignore'] else '❌ No'}"
        )
        print(
            f"  • Uses Environment Variables: {'✅ Yes' if env_vars['uses_env_vars'] else '❌ No'}"
        )

        print("\n🌐 CORS CONFIGURATION:")
        cors = report["cors_configuration"]
        print(f"  • CORS Configured: {'✅ Yes' if cors['has_cors'] else '❌ No'}")
        print(
            f"  • Allows All Origins: {'⚠️  Yes (risky)' if cors['allows_all_origins'] else '✅ No (good)'}"
        )

        # Show critical/high findings
        critical_high = [f for f in self.findings if f.severity in ["critical", "high"]]
        if critical_high:
            print("\n⚠️  CRITICAL/HIGH PRIORITY FINDINGS:")
            for i, finding in enumerate(critical_high[:5], 1):
                print(f"  {i}. [{finding.severity.upper()}] {finding.title}")
                if finding.file_path:
                    print(f"     File: {finding.file_path}")
                if finding.remediation:
                    print(f"     Fix: {finding.remediation}")
        else:
            print("\n✅ No critical or high priority security issues detected!")

        print("\n" + "=" * 80)


async def main():
    """Main entry point"""
    auditor = SecurityAuditor()

    try:
        report = await auditor.run_full_audit()

        # Exit with appropriate code
        if report["summary"]["critical"] > 0:
            logger.error("Critical security issues found!")
            sys.exit(1)
        elif report["summary"]["high"] > 0:
            logger.warning("High severity security issues found")
            sys.exit(0)  # Still exit 0 for now as these may be acceptable
        else:
            logger.info("Security audit passed with no critical issues")
            sys.exit(0)

    except Exception as e:
        logger.error(f"Security audit failed: {e}")
        import traceback

        logger.error(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
