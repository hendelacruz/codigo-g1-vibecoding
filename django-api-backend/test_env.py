#!/usr/bin/env python3

from decouple import config, Csv
import os

print("Testing environment configuration...")
print(f"Current working directory: {os.getcwd()}")
print(f".env file exists: {os.path.exists('.env')}")

print("\nTesting decouple config:")
try:
    debug = config('DEBUG', default=True, cast=bool)
    print(f"DEBUG value: {debug} (type: {type(debug)})")
    
    allowed_hosts = config('ALLOWED_HOSTS', default='localhost,127.0.0.1', cast=Csv())
    print(f"ALLOWED_HOSTS value: {allowed_hosts} (type: {type(allowed_hosts)})")
    
    secret_key = config('SECRET_KEY', default='default-key')
    print(f"SECRET_KEY found: {len(secret_key) > 0}")
    
except Exception as e:
    print(f"Error reading config: {e}")

print("\nReading .env file directly:")
if os.path.exists('.env'):
    with open('.env', 'r') as f:
        for line_num, line in enumerate(f, 1):
            if line.strip() and not line.strip().startswith('#'):
                key = line.split('=')[0] if '=' in line else ''
                if key in ['DEBUG', 'ALLOWED_HOSTS']:
                    print(f"Line {line_num}: {line.strip()}")