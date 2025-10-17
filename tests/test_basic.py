#!/usr/bin/env python3
"""
Basic tests for Nutrition Tracker
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_imports():
    """Test that we can import the app"""
    try:
        from app import app
        assert app is not None
        print("✅ App import successful")
        return True
    except Exception as e:
        print(f"❌ App import failed: {e}")
        return False

def test_health_endpoint():
    """Test health endpoint"""
    try:
        from app import app
        with app.test_client() as client:
            response = client.get('/health')
            assert response.status_code == 200
            data = response.get_json()
            assert data['status'] == 'healthy'
        print("✅ Health endpoint test passed")
        return True
    except Exception as e:
        print(f"❌ Health endpoint test failed: {e}")
        return False

def test_products_api():
    """Test products API"""
    try:
        from app import app
        with app.test_client() as client:
            response = client.get('/api/products')
            assert response.status_code == 200
            data = response.get_json()
            assert 'data' in data
            assert isinstance(data['data'], list)
        print("✅ Products API test passed")
        return True
    except Exception as e:
        print(f"❌ Products API test failed: {e}")
        return False

def test_main_page():
    """Test main page loads"""
    try:
        from app import app
        with app.test_client() as client:
            response = client.get('/')
            assert response.status_code == 200
            assert b'Nutrition Tracker' in response.data
        print("✅ Main page test passed")
        return True
    except Exception as e:
        print(f"❌ Main page test failed: {e}")
        return False

def run_tests():
    """Run all tests"""
    print("🧪 Running basic tests...")
    
    tests = [
        test_imports,
        test_health_endpoint,
        test_products_api,
        test_main_page
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        return True
    else:
        print("❌ Some tests failed!")
        return False

if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
