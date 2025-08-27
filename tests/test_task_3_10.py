#!/usr/bin/env python3
"""
Task 3.10 Verification Test
Verify Ollama Local LLM Fallback System implementation
"""

import asyncio
import sys
from pathlib import Path

# Add app directory to path
sys.path.append(str(Path(__file__).parent.parent))

async def test_ollama_integration():
    """Test Ollama integration components"""
    
    print("🧪 Testing Task 3.10: Ollama Local LLM Fallback System")
    print("=" * 60)
    
    tests_passed = 0
    tests_total = 0
    
    # Test 1: Import Ollama Service
    tests_total += 1
    try:
        from app.services.ollama_service import ollama_service, ollama_manager
        print("✅ Test 1: Ollama service imports successfully")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Test 1: Ollama service import failed: {e}")
    
    # Test 2: Import AI Router with Ollama
    tests_total += 1
    try:
        from app.services.ai_router import ai_router, generate_ai_response
        print("✅ Test 2: AI router with Ollama fallback imports successfully")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Test 2: AI router import failed: {e}")
    
    # Test 3: Import Base AI Service
    tests_total += 1
    try:
        from app.services.ai_service_base import BaseAIService, AIResponse, StreamingResponse
        print("✅ Test 3: Base AI service classes import successfully")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Test 3: Base AI service import failed: {e}")
    
    # Test 4: Ollama Service Configuration
    tests_total += 1
    try:
        from app.services.ollama_service import ollama_service
        assert ollama_service.service_name == "ollama"
        assert ollama_service.base_url == "http://localhost:11434"
        assert len(ollama_service.available_models) > 0
        print("✅ Test 4: Ollama service properly configured")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Test 4: Ollama configuration failed: {e}")
    
    # Test 5: AI Router Registration
    tests_total += 1
    try:
        from app.services.ai_router import ai_router
        assert "ollama" in ai_router.providers
        print("✅ Test 5: Ollama registered with AI router")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Test 5: AI router registration failed: {e}")
    
    # Test 6: Ollama Availability Check (without requiring server)
    tests_total += 1
    try:
        # This should not fail even if Ollama server is not running
        available = await ollama_service.check_availability()
        print(f"✅ Test 6: Ollama availability check completed (server {'available' if available else 'not running'})")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Test 6: Ollama availability check failed: {e}")
    
    # Test 7: Model Recommendations
    tests_total += 1
    try:
        model_en = ollama_service.get_recommended_model("en")
        model_fr = ollama_service.get_recommended_model("fr") 
        model_zh = ollama_service.get_recommended_model("zh")
        assert model_en in ["neural-chat:7b", "llama2:7b", "codellama:7b"]
        assert model_fr in ["mistral:7b", "llama2:7b"]
        print("✅ Test 7: Model recommendations working correctly")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Test 7: Model recommendations failed: {e}")
    
    # Test 8: Router Fallback Logic
    tests_total += 1
    try:
        from app.services.ai_router import ai_router
        # Test provider selection with force_local
        selection = await ai_router.select_provider(language="en", force_local=True)
        assert selection.provider_name == "ollama"
        assert selection.is_fallback == True
        print("✅ Test 8: Router fallback logic working")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Test 8: Router fallback logic failed: {e}")
    
    # Test 9: Setup Script Exists
    tests_total += 1
    try:
        setup_script = Path(__file__).parent.parent / "scripts" / "setup_ollama.py"
        assert setup_script.exists()
        print("✅ Test 9: Ollama setup script exists")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Test 9: Setup script check failed: {e}")
    
    # Test 10: Health Status Check
    tests_total += 1
    try:
        health = await ollama_service.get_health_status()
        assert "service_name" in health
        assert health["service_name"] == "ollama"
        print("✅ Test 10: Health status check working")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Test 10: Health status check failed: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print(f"📊 TEST SUMMARY: {tests_passed}/{tests_total} tests passed")
    
    # Clean up resources
    try:
        await ollama_service.close()
    except:
        pass  # Ignore cleanup errors
    
    if tests_passed == tests_total:
        print("🎉 ALL TESTS PASSED - Task 3.10 successfully implemented!")
        print("\n✨ Ollama Local LLM Fallback System is ready for use")
        return True
    else:
        print(f"⚠️  {tests_total - tests_passed} tests failed - implementation needs fixes")
        return False

async def main():
    """Main test function"""
    try:
        success = await test_ollama_integration()
        
        if success:
            print("\n🚀 Next Steps:")
            print("   1. Install Ollama: https://ollama.ai/")
            print("   2. Start Ollama server: 'ollama serve'")
            print("   3. Pull models: 'python scripts/setup_ollama.py setup'")
            print("   4. Test with: 'python scripts/setup_ollama.py test'")
        
        return success
        
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)