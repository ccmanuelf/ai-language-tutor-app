#!/usr/bin/env python3
"""
Environment Validation Script
MANDATORY: Run before ANY testing or validation
"""

import sys
import os
from pathlib import Path
import importlib.util


def validate_environment():
    """Comprehensive environment validation"""

    print("🔍 ENVIRONMENT VALIDATION - MANDATORY PRE-TEST CHECK")
    print("=" * 60)
    print()

    checks = []

    # Check 1: Python Environment Path
    print("1️⃣ PYTHON ENVIRONMENT CHECK")
    print("-" * 30)

    expected_path = "ai-language-tutor-app/ai-tutor-env"
    current_python = sys.executable

    if expected_path in current_python:
        print(f"✅ CORRECT: {current_python}")
        checks.append(("Python Environment", True, current_python))
    else:
        print(f"❌ WRONG: {current_python}")
        print(f"   Expected path containing: {expected_path}")
        print(f"   Run: source ai-tutor-env/bin/activate")
        checks.append(("Python Environment", False, f"Wrong path: {current_python}"))

    print()

    # Check 2: Critical Dependencies
    print("2️⃣ CRITICAL DEPENDENCIES CHECK")
    print("-" * 35)

    critical_deps = [
        ("pyaudio", "PyAudio"),
        ("numpy", "NumPy"),
        ("piper", "Piper TTS"),
        ("ibm_watson", "IBM Watson SDK"),
        ("mistralai", "Mistral AI"),
    ]

    deps_available = 0
    for module_name, display_name in critical_deps:
        try:
            spec = importlib.util.find_spec(module_name)
            if spec is not None:
                print(f"✅ {display_name}: Available")
                deps_available += 1
            else:
                print(f"❌ {display_name}: Not found")
        except ImportError:
            print(f"❌ {display_name}: Import error")

    deps_passed = deps_available == len(critical_deps)
    checks.append(
        (
            "Dependencies",
            deps_passed,
            f"{deps_available}/{len(critical_deps)} available",
        )
    )

    print()

    # Check 3: Working Directory
    print("3️⃣ WORKING DIRECTORY CHECK")
    print("-" * 30)

    current_dir = os.getcwd()
    if "ai-language-tutor-app" in current_dir:
        print(f"✅ CORRECT: {current_dir}")
        checks.append(("Working Directory", True, current_dir))
    else:
        print(f"❌ WRONG: {current_dir}")
        print(f"   Expected: path containing 'ai-language-tutor-app'")
        checks.append(("Working Directory", False, current_dir))

    print()

    # Check 4: Voice Models
    print("4️⃣ VOICE MODELS CHECK")
    print("-" * 25)

    voices_dir = Path("app/data/piper_voices")
    if voices_dir.exists():
        onnx_files = list(voices_dir.glob("*.onnx"))
        json_files = list(voices_dir.glob("*.onnx.json"))

        if len(onnx_files) >= 5 and len(json_files) >= 5:
            print(
                f"✅ SUFFICIENT: {len(onnx_files)} ONNX models, {len(json_files)} configs"
            )
            checks.append(("Voice Models", True, f"{len(onnx_files)} models"))
        else:
            print(
                f"⚠️  LIMITED: {len(onnx_files)} ONNX models, {len(json_files)} configs"
            )
            checks.append(("Voice Models", False, f"Only {len(onnx_files)} models"))
    else:
        print(f"❌ MISSING: {voices_dir} not found")
        checks.append(("Voice Models", False, "Directory missing"))

    print()

    # Check 5: Service Availability Test
    print("5️⃣ SERVICE AVAILABILITY TEST")
    print("-" * 32)

    try:
        # Quick service initialization test
        sys.path.append(".")
        from app.services.speech_processor import SpeechProcessor

        processor = SpeechProcessor()

        services = {
            "Mistral STT": processor.mistral_stt_available,
            "Piper TTS": processor.piper_tts_available,
            "Watson STT": processor.watson_stt_available,
            "Watson TTS": processor.watson_tts_available,
        }

        critical_services = ["Mistral STT", "Piper TTS"]
        critical_available = all(services[svc] for svc in critical_services)

        for service, available in services.items():
            status = "✅" if available else "❌"
            print(
                f"{status} {service}: {'Available' if available else 'Not Available'}"
            )

        checks.append(
            (
                "Service Availability",
                critical_available,
                f"{sum(services.values())}/{len(services)} services",
            )
        )

    except Exception as e:
        print(f"❌ Service test failed: {e}")
        checks.append(("Service Availability", False, f"Test failed: {e}"))

    print()

    # Final Results
    print("🎯 VALIDATION SUMMARY")
    print("=" * 25)

    passed_checks = sum(1 for _, passed, _ in checks if passed)
    total_checks = len(checks)

    for check_name, passed, details in checks:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {check_name}: {details}")

    print(f"\\nOverall: {passed_checks}/{total_checks} checks passed")

    if passed_checks == total_checks:
        print("\\n🎉 ENVIRONMENT VALIDATION: PASSED")
        print("🎉 Safe to proceed with testing and validation")
        return True
    else:
        print("\\n🚨 ENVIRONMENT VALIDATION: FAILED")
        print("🚨 DO NOT PROCEED - Fix issues above first")
        print("\\n📋 Common fixes:")
        print("   1. Activate virtual environment: source ai-tutor-env/bin/activate")
        print("   2. Install missing dependencies: pip install -r requirements.txt")
        print("   3. Change to project directory: cd ai-language-tutor-app")
        return False


def main():
    """Main validation entry point"""
    success = validate_environment()

    # Save validation results
    results_dir = Path("validation_results")
    results_dir.mkdir(exist_ok=True)

    import json
    from datetime import datetime

    result = {
        "timestamp": datetime.now().isoformat(),
        "validation_passed": success,
        "python_executable": sys.executable,
        "working_directory": os.getcwd(),
    }

    with open(results_dir / "last_environment_validation.json", "w") as f:
        json.dump(result, f, indent=2)

    if success:
        print(
            f"\\n📁 Validation results saved to: {results_dir}/last_environment_validation.json"
        )

    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
