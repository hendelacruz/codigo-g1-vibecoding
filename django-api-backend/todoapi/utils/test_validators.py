"""
Test file for custom validators.
Run with: python manage.py shell < todoapi/utils/test_validators.py
"""

from django.core.exceptions import ValidationError
from todoapi.utils.validators import (
    validate_ruc_peruano,
    validate_dni_peruano,
    validate_imei,
    validate_icc,
    validate_celular_peruano,
    validate_placa_peruana
)

def test_validators():
    """Test all custom validators with valid and invalid data."""
    
    print("=== TESTING CUSTOM VALIDATORS ===\n")
    
    # Test RUC Peruano
    print("1. Testing RUC Peruano:")
    valid_rucs = ["20123456789", "10123456789"]
    invalid_rucs = ["123456789", "1234567890123", "11111111111", "20123456788"]
    
    for ruc in valid_rucs:
        try:
            validate_ruc_peruano(ruc)
            print(f"  ✓ Valid RUC: {ruc}")
        except ValidationError as e:
            print(f"  ✗ Unexpected error for {ruc}: {e}")
    
    for ruc in invalid_rucs:
        try:
            validate_ruc_peruano(ruc)
            print(f"  ✗ Should have failed for {ruc}")
        except ValidationError:
            print(f"  ✓ Correctly rejected: {ruc}")
    
    # Test DNI Peruano
    print("\n2. Testing DNI Peruano:")
    valid_dnis = ["12345678", "87654321", "45678912"]
    invalid_dnis = ["1234567", "123456789", "00000000", "01234567"]
    
    for dni in valid_dnis:
        try:
            validate_dni_peruano(dni)
            print(f"  ✓ Valid DNI: {dni}")
        except ValidationError as e:
            print(f"  ✗ Unexpected error for {dni}: {e}")
    
    for dni in invalid_dnis:
        try:
            validate_dni_peruano(dni)
            print(f"  ✗ Should have failed for {dni}")
        except ValidationError:
            print(f"  ✓ Correctly rejected: {dni}")
    
    # Test IMEI
    print("\n3. Testing IMEI:")
    valid_imeis = ["123456789012345"]  # Note: This might not pass Luhn, but tests length
    invalid_imeis = ["12345678901234", "1234567890123456", "111111111111111"]
    
    for imei in valid_imeis:
        try:
            validate_imei(imei)
            print(f"  ✓ Valid IMEI: {imei}")
        except ValidationError as e:
            print(f"  ✗ Error for {imei}: {e}")
    
    for imei in invalid_imeis:
        try:
            validate_imei(imei)
            print(f"  ✗ Should have failed for {imei}")
        except ValidationError:
            print(f"  ✓ Correctly rejected: {imei}")
    
    # Test ICC
    print("\n4. Testing ICC:")
    valid_iccs = ["12345678901234567890", "ABCD1234EFGH5678IJKL"]
    invalid_iccs = ["1234567890123456789", "123456789012345678901", "AAAAAAAAAAAAAAAAAAAA"]
    
    for icc in valid_iccs:
        try:
            validate_icc(icc)
            print(f"  ✓ Valid ICC: {icc}")
        except ValidationError as e:
            print(f"  ✗ Unexpected error for {icc}: {e}")
    
    for icc in invalid_iccs:
        try:
            validate_icc(icc)
            print(f"  ✗ Should have failed for {icc}")
        except ValidationError:
            print(f"  ✓ Correctly rejected: {icc}")
    
    # Test Celular Peruano
    print("\n5. Testing Celular Peruano:")
    valid_celulares = ["987654321", "912345678", "999888777"]
    invalid_celulares = ["87654321", "9876543210", "123456789", "999999999"]
    
    for celular in valid_celulares:
        try:
            validate_celular_peruano(celular)
            print(f"  ✓ Valid Celular: {celular}")
        except ValidationError as e:
            print(f"  ✗ Unexpected error for {celular}: {e}")
    
    for celular in invalid_celulares:
        try:
            validate_celular_peruano(celular)
            print(f"  ✗ Should have failed for {celular}")
        except ValidationError:
            print(f"  ✓ Correctly rejected: {celular}")
    
    # Test Placa Peruana
    print("\n6. Testing Placa Peruana:")
    valid_placas = ["ABC-123", "XYZ-1234", "DEF-567"]
    invalid_placas = ["AB-123", "ABC-12", "ABCD-123", "ABC123"]
    
    for placa in valid_placas:
        try:
            validate_placa_peruana(placa)
            print(f"  ✓ Valid Placa: {placa}")
        except ValidationError as e:
            print(f"  ✗ Unexpected error for {placa}: {e}")
    
    for placa in invalid_placas:
        try:
            validate_placa_peruana(placa)
            print(f"  ✗ Should have failed for {placa}")
        except ValidationError:
            print(f"  ✓ Correctly rejected: {placa}")
    
    print("\n=== VALIDATOR TESTING COMPLETED ===")

if __name__ == "__main__":
    test_validators()