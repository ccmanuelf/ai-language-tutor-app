"""
Quick test to verify /languages endpoint returns all 8 languages with support_level
"""

import json

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

print("=" * 60)
print("Testing /api/v1/conversations/languages endpoint")
print("=" * 60)

response = client.get("/api/v1/conversations/languages")

print(f"\nStatus Code: {response.status_code}")

if response.status_code == 200:
    data = response.json()

    print(f"\n✅ Total Languages: {data.get('total', 0)}")
    print(f"\nSupport Levels Defined:")
    for level, desc in data.get("support_levels", {}).items():
        print(f"  - {level}: {desc}")

    print(f"\n📋 Languages List:")
    print("-" * 60)

    for lang in data.get("languages", []):
        print(
            f"\n{lang['code'].upper()}: {lang['name']} ({lang.get('native_name', 'N/A')})"
        )
        print(f"  Support Level: {lang.get('support_level', 'UNKNOWN')}")
        print(f"  TTS: {'✅' if lang.get('has_tts') else '❌'}")
        print(f"  STT: {'✅' if lang.get('has_stt') else '❌'}")
        print(f"  Display: {lang.get('display', 'N/A')}")

        if "warning" in lang:
            print(f"  ⚠️  WARNING: {lang['warning']}")
            print(f"  Limitations:")
            for limitation in lang.get("limitations", []):
                print(f"    - {limitation}")

    print("\n" + "=" * 60)
    print("VERIFICATION:")
    print("=" * 60)

    # Check for Italian and Portuguese
    codes = [l["code"] for l in data.get("languages", [])]
    print(f"\n✅ Italian (it) present: {'it' in codes}")
    print(f"✅ Portuguese (pt) present: {'pt' in codes}")
    print(f"✅ Total count = 8: {data.get('total') == 8}")

    # Check for Japanese warning
    ja_lang = next((l for l in data.get("languages", []) if l["code"] == "ja"), None)
    if ja_lang:
        print(f"✅ Japanese has warning: {'warning' in ja_lang}")
        print(
            f"✅ Japanese support_level = STT_ONLY: {ja_lang.get('support_level') == 'STT_ONLY'}"
        )

    # Full language codes
    print(f"\nAll language codes: {codes}")

else:
    print(f"\n❌ Error: {response.text}")
