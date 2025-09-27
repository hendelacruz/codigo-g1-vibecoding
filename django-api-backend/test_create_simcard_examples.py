#!/usr/bin/env python3
"""
Ejemplos de pruebas para crear SIM cards via API
Este archivo contiene diferentes escenarios de prueba para demostrar
cómo crear SIM cards usando la API REST de Django.
"""

import requests
import json
from datetime import datetime, timezone
import sys

# Configuration
BASE_URL = "http://127.0.0.1:8000"
API_ENDPOINT = f"{BASE_URL}/api/inventory/simcards/"

def print_separator(title):
    """Print a formatted separator for test sections"""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def print_test_result(test_name, response):
    """Print formatted test results"""
    print(f"\n🧪 Test: {test_name}")
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 201:
        print("✅ SUCCESS - SIM card created successfully!")
        data = response.json()
        print(f"📱 Created SIM card ID: {data.get('id')}")
        print(f"📱 ICC: {data.get('icc')}")
        print(f"📱 Chip Number: {data.get('numero_chip')}")
        print(f"📱 Estado: {data.get('estado')}")
        print(f"📱 Proceso: {data.get('proceso')}")
    else:
        print("❌ FAILED")
        try:
            error_data = response.json()
            print(f"Error details: {json.dumps(error_data, indent=2)}")
        except:
            print(f"Error text: {response.text}")

def test_create_simcard_minimal_data():
    """Test 1: Create SIM card with minimal required data"""
    print_separator("TEST 1: Crear SIM card con datos mínimos")
    
    # Minimal data required
    simcard_data = {
        "fecha_compra": "2025-01-15T10:30:00Z",
        "numero_factura": "F001-2025-001",
        "numero_chip": "123456789",
        "icc": "89511234567890123456",  # Exactly 20 characters
        "proveedor": 1  # Assuming proveedor with ID 1 exists
    }
    
    print("📋 Data to send:")
    print(json.dumps(simcard_data, indent=2))
    
    try:
        response = requests.post(
            API_ENDPOINT,
            json=simcard_data,
            headers={"Content-Type": "application/json"}
        )
        print_test_result("Minimal Data Creation", response)
        return response.json() if response.status_code == 201 else None
        
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Cannot connect to server. Make sure Django server is running!")
        return None
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return None

def test_create_simcard_complete_data():
    """Test 2: Create SIM card with complete data"""
    print_separator("TEST 2: Crear SIM card con datos completos")
    
    # Complete data including optional fields
    simcard_data = {
        "fecha_compra": "2025-01-15T14:45:00Z",
        "numero_factura": "F001-2025-002",
        "numero_chip": "987654321",
        "icc": "89511234567890123457",  # Different ICC
        "proveedor": 1,
        "cliente": None,  # Explicitly set to None
        "estado": "no_asignado",  # Explicit state
        "proceso": "en_produccion",  # Explicit process
        "is_active": True,  # Explicit active status
        "observaciones": "SIM card de prueba con datos completos"
    }
    
    print("📋 Data to send:")
    print(json.dumps(simcard_data, indent=2))
    
    try:
        response = requests.post(
            API_ENDPOINT,
            json=simcard_data,
            headers={"Content-Type": "application/json"}
        )
        print_test_result("Complete Data Creation", response)
        return response.json() if response.status_code == 201 else None
        
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Cannot connect to server. Make sure Django server is running!")
        return None
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return None

def test_create_simcard_invalid_icc():
    """Test 3: Test validation with invalid ICC"""
    print_separator("TEST 3: Probar validación con ICC inválido")
    
    # Invalid ICC (wrong length)
    simcard_data = {
        "fecha_compra": "2025-01-15T16:00:00Z",
        "numero_factura": "F001-2025-003",
        "numero_chip": "555666777",
        "icc": "123456789",  # Too short (9 characters instead of 20)
        "proveedor": 1
    }
    
    print("📋 Data to send (with invalid ICC):")
    print(json.dumps(simcard_data, indent=2))
    
    try:
        response = requests.post(
            API_ENDPOINT,
            json=simcard_data,
            headers={"Content-Type": "application/json"}
        )
        print_test_result("Invalid ICC Validation", response)
        
        if response.status_code == 400:
            print("✅ Validation working correctly - ICC error detected!")
        
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Cannot connect to server. Make sure Django server is running!")
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")

def test_create_simcard_missing_fields():
    """Test 4: Test validation with missing required fields"""
    print_separator("TEST 4: Probar validación con campos requeridos faltantes")
    
    # Missing required fields
    simcard_data = {
        "numero_chip": "111222333",
        # Missing: fecha_compra, numero_factura, icc, proveedor
    }
    
    print("📋 Data to send (missing required fields):")
    print(json.dumps(simcard_data, indent=2))
    
    try:
        response = requests.post(
            API_ENDPOINT,
            json=simcard_data,
            headers={"Content-Type": "application/json"}
        )
        print_test_result("Missing Fields Validation", response)
        
        if response.status_code == 400:
            print("✅ Validation working correctly - Missing fields detected!")
        
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Cannot connect to server. Make sure Django server is running!")
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")

def test_list_simcards():
    """Test 5: List all SIM cards to verify creation"""
    print_separator("TEST 5: Listar todas las SIM cards creadas")
    
    try:
        response = requests.get(API_ENDPOINT)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ SUCCESS - Found {len(data.get('results', []))} SIM cards")
            
            for simcard in data.get('results', [])[:3]:  # Show first 3
                print(f"📱 ID: {simcard.get('id')} | ICC: {simcard.get('icc')} | Estado: {simcard.get('estado')}")
        else:
            print("❌ FAILED to retrieve SIM cards")
            print(f"Error: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Cannot connect to server. Make sure Django server is running!")
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")

def main():
    """Run all test scenarios"""
    print_separator("🧪 PRUEBAS PARA CREAR SIM CARDS VIA API")
    print("Este script ejecuta diferentes escenarios de prueba para demostrar")
    print("cómo crear SIM cards usando la API REST de Django.")
    print(f"🌐 API Endpoint: {API_ENDPOINT}")
    
    # Check if server is running
    try:
        response = requests.get(BASE_URL, timeout=5)
        print("✅ Server is running!")
    except:
        print("❌ ERROR: Django server is not running!")
        print("Please start the server with: python manage.py runserver 8000")
        sys.exit(1)
    
    # Run tests
    test_create_simcard_minimal_data()
    test_create_simcard_complete_data()
    test_create_simcard_invalid_icc()
    test_create_simcard_missing_fields()
    test_list_simcards()
    
    print_separator("🎉 PRUEBAS COMPLETADAS")
    print("Revisa los resultados arriba para ver cómo funcionan las validaciones")
    print("y la creación de SIM cards via API.")

if __name__ == "__main__":
    main()