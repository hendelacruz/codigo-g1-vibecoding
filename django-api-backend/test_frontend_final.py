#!/usr/bin/env python
"""
Test final completo para verificar acceso frontend a la API de clientes.
Incluye CORS, autenticación, CRUD y validaciones.
"""

import requests
import json
import random
import string

# Configuration
BASE_URL = "http://127.0.0.1:8000"
API_URL = f"{BASE_URL}/api"

def generate_unique_ruc():
    """Generate a unique valid RUC for testing"""
    # Generate base RUC (10 digits)
    base = "2055566" + ''.join(random.choices(string.digits, k=3))
    
    # Calculate check digit using Peruvian algorithm
    factors = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]
    total = sum(int(digit) * factor for digit, factor in zip(base, factors))
    remainder = total % 11
    check_digit = 11 - remainder if remainder >= 2 else remainder
    
    return base + str(check_digit)

def test_cors_functionality():
    """Test CORS headers and preflight requests"""
    print("🧪 TESTING CORS FUNCTIONALITY")
    print("=" * 60)
    
    url = f"{API_URL}/entities/clientes/"
    
    try:
        # Test OPTIONS request (preflight)
        headers = {
            'Origin': 'http://localhost:3000',
            'Access-Control-Request-Method': 'GET',
            'Access-Control-Request-Headers': 'authorization,content-type'
        }
        
        response = requests.options(url, headers=headers)
        
        print(f"✅ OPTIONS Status: {response.status_code}")
        
        # Check essential CORS headers
        cors_headers = {
            'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
            'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
            'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers'),
            'Access-Control-Allow-Credentials': response.headers.get('Access-Control-Allow-Credentials')
        }
        
        all_present = True
        for header, value in cors_headers.items():
            if value:
                print(f"✅ {header}: {value}")
            else:
                print(f"❌ {header}: Missing")
                all_present = False
        
        return all_present
        
    except Exception as e:
        print(f"❌ CORS test error: {e}")
        return False

def test_authentication():
    """Test authentication functionality"""
    print("\n🧪 TESTING AUTHENTICATION")
    print("=" * 60)
    
    login_url = f"{API_URL}/auth/login/"
    
    # Test valid login
    login_data = {
        "username": "Hdelacruz",
        "password": "Hygcompe2025"
    }
    
    try:
        response = requests.post(login_url, json=login_data)
        
        if response.status_code == 200:
            data = response.json()
            if 'access' in data:
                print(f"✅ Login successful: {data.get('user', {}).get('username', 'Unknown')}")
                return data['access']
            else:
                print("❌ Login response missing access token")
                return None
        else:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return None

def test_clientes_access(token):
    """Test access to clientes endpoints"""
    print("\n🧪 TESTING CLIENTES ACCESS")
    print("=" * 60)
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
        'Origin': 'http://localhost:3000'
    }
    
    # Test GET clientes list
    try:
        url = f"{API_URL}/entities/clientes/"
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Clientes list: {data.get('count', 0)} total clientes")
            
            # Check CORS headers in actual response
            cors_present = any('access-control' in h.lower() for h in response.headers.keys())
            if cors_present:
                print("✅ CORS headers present in response")
            else:
                print("⚠️  CORS headers not found in response")
            
            return True
        else:
            print(f"❌ Clientes access failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Clientes access error: {e}")
        return False

def test_cliente_crud(token):
    """Test CRUD operations on clientes"""
    print("\n🧪 TESTING CLIENTE CRUD OPERATIONS")
    print("=" * 60)
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
        'Origin': 'http://localhost:3000'
    }
    
    # Generate unique data for testing
    unique_ruc = generate_unique_ruc()
    unique_phone = f"9{random.randint(10000000, 99999999)}"
    unique_email = f"test{random.randint(1000, 9999)}@example.com"
    
    # Test CREATE
    try:
        url = f"{API_URL}/entities/clientes/"
        cliente_data = {
            "nombre": "Cliente Test Frontend",
            "ruc": unique_ruc,
            "celular": unique_phone,
            "correo": unique_email,
            "direccion": "Dirección Test 123",
            "contacto": "Juan Pérez",
            "activo": True
        }
        
        response = requests.post(url, json=cliente_data, headers=headers)
        
        if response.status_code == 201:
            created_cliente = response.json()
            cliente_id = created_cliente['id']
            print(f"✅ Cliente created: ID {cliente_id}, RUC {unique_ruc}")
            
            # Test UPDATE
            update_data = {
                "nombre": "Cliente Test Frontend Updated",
                "ruc": unique_ruc,
                "celular": unique_phone,
                "correo": unique_email,
                "direccion": "Dirección Actualizada 456",
                "activo": True
            }
            
            update_response = requests.put(f"{url}{cliente_id}/", json=update_data, headers=headers)
            
            if update_response.status_code == 200:
                print("✅ Cliente updated successfully")
                
                # Test DELETE
                delete_response = requests.delete(f"{url}{cliente_id}/", headers=headers)
                
                if delete_response.status_code == 204:
                    print("✅ Cliente deleted successfully")
                    return True
                else:
                    print(f"❌ Delete failed: {delete_response.status_code}")
                    return False
            else:
                print(f"❌ Update failed: {update_response.status_code}")
                return False
        else:
            print(f"❌ Create failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ CRUD error: {e}")
        return False

def test_validation_errors(token):
    """Test validation error handling"""
    print("\n🧪 TESTING VALIDATION ERRORS")
    print("=" * 60)
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
        'Origin': 'http://localhost:3000'
    }
    
    # Test with invalid data
    try:
        url = f"{API_URL}/entities/clientes/"
        invalid_data = {
            "nombre": "",  # Empty name
            "ruc": "invalid",  # Invalid RUC
            "celular": "123",  # Invalid phone
            "correo": "invalid-email",  # Invalid email
        }
        
        response = requests.post(url, json=invalid_data, headers=headers)
        
        if response.status_code == 400:
            errors = response.json()
            error_fields = list(errors.keys())
            print(f"✅ Validation errors caught: {error_fields}")
            return True
        else:
            print(f"❌ Expected validation errors, got: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Validation test error: {e}")
        return False

def test_search_and_filters(token):
    """Test search and filter functionality"""
    print("\n🧪 TESTING SEARCH AND FILTERS")
    print("=" * 60)
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
        'Origin': 'http://localhost:3000'
    }
    
    try:
        # Test search
        url = f"{API_URL}/entities/clientes/?search=Cliente"
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Search results: {data.get('count', 0)} clientes found")
            
            # Test active filter
            url = f"{API_URL}/entities/clientes/?activo=true"
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Active filter: {data.get('count', 0)} active clientes")
                return True
            else:
                print(f"❌ Filter failed: {response.status_code}")
                return False
        else:
            print(f"❌ Search failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Search/filter error: {e}")
        return False

def main():
    """Run all frontend access tests"""
    print("🚀 COMPREHENSIVE FRONTEND ACCESS TEST")
    print("=" * 60)
    print("Testing complete frontend integration with Django API")
    print("=" * 60)
    
    results = []
    
    # Test 1: CORS functionality
    results.append(("CORS Functionality", test_cors_functionality()))
    
    # Test 2: Authentication
    token = test_authentication()
    if token:
        results.append(("Authentication", True))
        
        # Test 3: Basic access
        results.append(("Clientes Access", test_clientes_access(token)))
        
        # Test 4: CRUD operations
        results.append(("CRUD Operations", test_cliente_crud(token)))
        
        # Test 5: Validation errors
        results.append(("Validation Errors", test_validation_errors(token)))
        
        # Test 6: Search and filters
        results.append(("Search & Filters", test_search_and_filters(token)))
    else:
        results.append(("Authentication", False))
        print("⚠️  Skipping remaining tests due to authentication failure")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 FINAL TEST RESULTS")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Frontend can successfully access the clientes API")
        print("✅ CORS is properly configured")
        print("✅ Authentication works correctly")
        print("✅ CRUD operations are functional")
        print("✅ Validation and filters work as expected")
    elif passed >= total * 0.8:
        print("\n✅ MOSTLY WORKING!")
        print("Frontend access is functional with minor issues")
    else:
        print("\n❌ SIGNIFICANT ISSUES FOUND")
        print("Frontend access has major problems that need attention")

if __name__ == "__main__":
    main()