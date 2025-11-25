#!/usr/bin/env python3
"""
Diagnostic script to identify issues with the application.
"""

import sys
import os

print("=" * 80)
print("JUDICIAL PROCESS VERIFICATION ENGINE - DIAGNOSTIC SCRIPT")
print("=" * 80)
print()

# Check Python version
print("1. Python Version")
print(f"   Version: {sys.version}")
print(f"   Status: {'✓ OK' if sys.version_info >= (3, 11) else '✗ FAILED - Python 3.11+ required'}")
print()

# Check dependencies
print("2. Dependencies Check")
dependencies = [
    'fastapi', 'uvicorn', 'pydantic', 'pydantic_settings',
    'anthropic', 'requests', 'streamlit'
]

for dep in dependencies:
    try:
        __import__(dep)
        print(f"   {dep}: ✓ Installed")
    except ImportError:
        print(f"   {dep}: ✗ MISSING - Run: pip install -r requirements.txt")
print()

# Check environment file
print("3. Environment Configuration")
if os.path.exists('.env'):
    print("   .env file: ✓ Found")
    try:
        from dotenv import load_dotenv
        load_dotenv()
        from src.core.infrastructure.config import settings
        print(f"   API Title: {settings.API_TITLE}")
        print(f"   Debug Mode: {settings.DEBUG}")
        print(f"   Log Level: {settings.LOG_LEVEL}")
        if settings.ANTHROPIC_API_KEY:
            print(f"   ANTHROPIC_API_KEY: ✓ Configured")
        else:
            print(f"   ANTHROPIC_API_KEY: ⚠ Not set (demo mode will work)")
    except Exception as e:
        print(f"   Configuration Error: {e}")
else:
    print("   .env file: ✗ NOT FOUND")
    print("   Please copy env-example to .env: cp env-example .env")
print()

# Check source files
print("4. Source Code Files")
files_to_check = [
    'src/core/domain/entities.py',
    'src/core/domain/policy.py',
    'src/core/application/services/policy_service.py',
    'src/core/application/services/verification_service.py',
    'src/api/routers/health_router.py',
    'src/api/routers/verification_router.py',
    'src/entrypoints/main_api.py',
]

for file in files_to_check:
    if os.path.exists(file):
        print(f"   {file}: ✓")
    else:
        print(f"   {file}: ✗ MISSING")
print()

# Try to import main components
print("5. Application Imports")
try:
    from src.entrypoints.main_api import app
    print("   main_api.app: ✓ Importable")
except Exception as e:
    print(f"   main_api.app: ✗ Import failed: {e}")

try:
    from src.entrypoints.main_ui import st
    print("   main_ui: ✓ Importable (Streamlit UI ready)")
except Exception as e:
    print(f"   main_ui: ✗ Import failed: {e}")
print()

# Test health endpoint
print("6. API Health Check")
try:
    from src.entrypoints.main_api import app
    from fastapi.testclient import TestClient
    
    client = TestClient(app)
    response = client.get("/health")
    
    if response.status_code == 200:
        print(f"   Health Endpoint: ✓ OK (Status: {response.status_code})")
        print(f"   Response: {response.json()}")
    else:
        print(f"   Health Endpoint: ✗ Failed (Status: {response.status_code})")
except Exception as e:
    print(f"   Health Endpoint: ✗ Error: {e}")
print()

# Test verification endpoint with example
print("7. API Verification Endpoint")
try:
    from src.entrypoints.main_api import app
    from fastapi.testclient import TestClient
    import json
    
    client = TestClient(app)
    
    # Load example
    with open('examples/test_process_approved.json', 'r') as f:
        example = json.load(f)
    
    response = client.post("/v1/verify", json=example)
    
    if response.status_code == 200:
        result = response.json()
        print(f"   Verification Endpoint: ✓ OK")
        print(f"   Decision: {result.get('decision')}")
        print(f"   Process: {result.get('process_number')}")
    else:
        print(f"   Verification Endpoint: ✗ Failed (Status: {response.status_code})")
        print(f"   Response: {response.text}")
except Exception as e:
    print(f"   Verification Endpoint: ✗ Error: {e}")
print()

# Summary
print("=" * 80)
print("DIAGNOSTIC COMPLETE")
print("=" * 80)
print()
print("Next Steps:")
print("1. If .env is missing, copy it: cp env-example .env")
print("2. If dependencies are missing, install them: pip install -r requirements.txt")
print("3. To run the API: python run_api.py")
print("4. To run the UI: python run_ui.py")
print("5. To run with Docker: docker-compose up")
print()

