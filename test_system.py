"""
Test toàn bộ hệ thống AI Legal Assistant
"""
import os
import sys
from pathlib import Path

# Add src to path
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

def test_basic_question():
    """Test câu hỏi cơ bản"""
    from src.run_cli import main as run_cli
    
    print("🧪 Test câu hỏi cơ bản...")
    
    # Mock sys.argv for testing
    original_argv = sys.argv
    sys.argv = ["run_cli.py", "Tuổi kết hôn tối thiểu ở Việt Nam là bao nhiêu?"]
    
    try:
        result = run_cli()
        print("✅ Test thành công!")
        return True
    except Exception as e:
        print(f"❌ Test thất bại: {e}")
        return False
    finally:
        sys.argv = original_argv

def main():
    """Chạy tất cả tests"""
    print("🚀 AI Legal Assistant - System Test")
    print("=" * 50)
    
    tests = [
        ("Kiểm tra hệ thống", lambda: os.system("python check_system.py") == 0),
        ("Build vector index", lambda: os.system("python rebuild_index.py") == 0), 
        ("Test câu hỏi cơ bản", test_basic_question),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 {test_name}...")
        try:
            if test_func():
                print(f"✅ {test_name}: PASSED")
                passed += 1
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
    
    print(f"\n📊 Kết quả: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 Tất cả tests PASSED! Hệ thống hoạt động tốt.")
        return 0
    else:
        print("⚠️ Một số tests FAILED. Vui lòng kiểm tra lại.")
        return 1

if __name__ == "__main__":
    sys.exit(main())