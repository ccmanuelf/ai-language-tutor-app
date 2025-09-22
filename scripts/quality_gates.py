#!/usr/bin/env python3
"""
Automated Quality Gates System
MANDATORY: Run before marking any task as COMPLETED
"""

import sys
import json
from pathlib import Path
from datetime import datetime
import subprocess


class QualityGateValidator:
    """Automated quality gate validation system"""

    def __init__(self, task_id, artifacts_dir="validation_artifacts"):
        self.task_id = task_id
        self.artifacts_dir = Path(artifacts_dir) / task_id
        self.results = {
            "task_id": task_id,
            "timestamp": datetime.now().isoformat(),
            "gates": {},
            "overall_passed": False,
        }

    def gate_1_evidence_collection(self):
        """Gate 1: Verify tangible evidence exists"""
        print("🚨 GATE 1: EVIDENCE COLLECTION")
        print("-" * 35)

        if not self.artifacts_dir.exists():
            print(f"❌ Artifacts directory missing: {self.artifacts_dir}")
            return False

        # Find all artifact files
        artifacts = list(self.artifacts_dir.glob("*"))
        large_files = [f for f in artifacts if f.stat().st_size > 1024]  # >1KB

        print(f"📁 Artifacts directory: {self.artifacts_dir}")
        print(f"📄 Total files: {len(artifacts)}")
        print(f"📊 Files >1KB: {len(large_files)}")

        for f in large_files:
            size_kb = f.stat().st_size / 1024
            print(f"   ✅ {f.name} ({size_kb:.1f} KB)")

        # Requirements: At least 3 substantial files
        passed = len(large_files) >= 3

        if passed:
            print("✅ GATE 1 PASSED: Sufficient evidence collected")
        else:
            print("❌ GATE 1 FAILED: Insufficient evidence (need ≥3 files >1KB)")

        self.results["gates"]["evidence_collection"] = {
            "passed": passed,
            "files_count": len(artifacts),
            "substantial_files": len(large_files),
            "files": [str(f) for f in large_files],
        }

        return passed

    def gate_2_functional_verification(self):
        """Gate 2: Verify functional requirements"""
        print("\\n🚨 GATE 2: FUNCTIONAL VERIFICATION")
        print("-" * 38)

        # Check for audio files (speech tasks)
        audio_files = list(self.artifacts_dir.glob("*.wav"))

        if audio_files:
            print("🎵 Audio Files Found:")
            valid_audio = 0

            for audio_file in audio_files:
                try:
                    import wave

                    with wave.open(str(audio_file), "rb") as wav:
                        frames = wav.getnframes()
                        rate = wav.getframerate()
                        duration = frames / rate

                    if duration > 0.5 and rate >= 16000:
                        print(f"   ✅ {audio_file.name}: {duration:.1f}s, {rate}Hz")
                        valid_audio += 1
                    else:
                        print(f"   ❌ {audio_file.name}: Invalid format")

                except Exception as e:
                    print(f"   ❌ {audio_file.name}: Read error - {e}")

            audio_passed = valid_audio >= 3
            print(f"🎯 Valid audio files: {valid_audio}/{len(audio_files)}")

        else:
            print("ℹ️  No audio files found (may not be audio task)")
            audio_passed = True  # Not applicable for non-audio tasks

        # Check for test results files
        test_files = list(self.artifacts_dir.glob("*test*")) + list(
            self.artifacts_dir.glob("*result*")
        )
        test_passed = len(test_files) > 0

        if test_passed:
            print(f"✅ Test result files found: {len(test_files)}")
        else:
            print("❌ No test result files found")

        overall_passed = audio_passed and test_passed

        if overall_passed:
            print("✅ GATE 2 PASSED: Functional verification complete")
        else:
            print("❌ GATE 2 FAILED: Functional verification incomplete")

        self.results["gates"]["functional_verification"] = {
            "passed": overall_passed,
            "audio_files_valid": valid_audio if audio_files else "N/A",
            "test_files_found": len(test_files),
        }

        return overall_passed

    def gate_3_environment_validation(self):
        """Gate 3: Environment consistency check"""
        print("\\n🚨 GATE 3: ENVIRONMENT VALIDATION")
        print("-" * 36)

        # Run environment validation script
        try:
            result = subprocess.run(
                [sys.executable, "scripts/validate_environment.py"],
                capture_output=True,
                text=True,
                cwd=".",
            )

            env_passed = result.returncode == 0

            if env_passed:
                print("✅ Environment validation passed")
            else:
                print("❌ Environment validation failed")
                print("STDOUT:", result.stdout[-200:])  # Last 200 chars
                print("STDERR:", result.stderr[-200:])

        except Exception as e:
            print(f"❌ Environment validation error: {e}")
            env_passed = False

        if env_passed:
            print("✅ GATE 3 PASSED: Environment is consistent")
        else:
            print("❌ GATE 3 FAILED: Environment issues detected")

        self.results["gates"]["environment_validation"] = {"passed": env_passed}

        return env_passed

    def gate_4_reproducibility(self):
        """Gate 4: Reproducibility verification"""
        print("\\n🚨 GATE 4: REPRODUCIBILITY")
        print("-" * 28)

        # Check for test scripts
        test_scripts = (
            list(Path(".").glob("test_*.py"))
            + list(Path(".").glob("*_test.py"))
            + list(self.artifacts_dir.glob("*.py"))
        )

        script_exists = len(test_scripts) > 0
        print(f"🐍 Test scripts found: {len(test_scripts)}")

        # Check for documentation
        docs = (
            list(Path("docs").glob("*.md"))
            + list(self.artifacts_dir.glob("*.md"))
            + list(self.artifacts_dir.glob("*.txt"))
        )

        docs_exist = len(docs) > 0
        print(f"📚 Documentation files: {len(docs)}")

        # Check for clear instructions
        readme_files = list(Path(".").glob("README*")) + list(
            Path("docs").glob("*README*")
        )
        readme_exists = len(readme_files) > 0
        print(f"📖 README files: {len(readme_files)}")

        reproducibility_passed = script_exists and docs_exist

        if reproducibility_passed:
            print("✅ GATE 4 PASSED: Reproducibility requirements met")
        else:
            print("❌ GATE 4 FAILED: Missing reproducibility elements")

        self.results["gates"]["reproducibility"] = {
            "passed": reproducibility_passed,
            "test_scripts": len(test_scripts),
            "documentation": len(docs),
            "readme_files": len(readme_files),
        }

        return reproducibility_passed

    def run_all_gates(self):
        """Run all quality gates"""
        print("🔒 QUALITY GATES VALIDATION SYSTEM")
        print("=" * 50)
        print(f"Task ID: {self.task_id}")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        # Run all gates
        gate_results = [
            self.gate_1_evidence_collection(),
            self.gate_2_functional_verification(),
            self.gate_3_environment_validation(),
            self.gate_4_reproducibility(),
        ]

        passed_gates = sum(gate_results)
        total_gates = len(gate_results)

        print("\\n" + "=" * 50)
        print("🎯 QUALITY GATES SUMMARY")
        print("=" * 50)

        gate_names = [
            "Evidence Collection",
            "Functional Verification",
            "Environment Validation",
            "Reproducibility",
        ]

        for i, (name, passed) in enumerate(zip(gate_names, gate_results)):
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"Gate {i + 1}: {status} {name}")

        print(f"\\nOverall: {passed_gates}/{total_gates} gates passed")

        self.results["overall_passed"] = passed_gates == total_gates
        self.results["gates_passed"] = passed_gates
        self.results["gates_total"] = total_gates

        # Save results
        results_dir = Path("validation_results")
        results_dir.mkdir(exist_ok=True)

        results_file = results_dir / f"quality_gates_{self.task_id}.json"
        with open(results_file, "w") as f:
            json.dump(self.results, f, indent=2)

        if self.results["overall_passed"]:
            print(f"\\n🎉 ALL QUALITY GATES PASSED")
            print(f"🎉 Task {self.task_id} is ready for COMPLETION")
            print(f"📁 Results saved: {results_file}")
            return True
        else:
            print(f"\\n🚨 QUALITY GATES FAILED")
            print(f"🚨 Task {self.task_id} is NOT ready for completion")
            print(f"🚨 Fix failing gates before marking as COMPLETED")
            print(f"📁 Results saved: {results_file}")
            return False


def main():
    """Main quality gates runner"""
    if len(sys.argv) != 2:
        print("Usage: python scripts/quality_gates.py <task_id>")
        print("Example: python scripts/quality_gates.py 2A.3")
        sys.exit(1)

    task_id = sys.argv[1]
    validator = QualityGateValidator(task_id)
    success = validator.run_all_gates()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
