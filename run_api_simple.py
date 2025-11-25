#!/usr/bin/env python3
"""
Simple test to run the API with detailed error information.
"""
import sys
import traceback

print("=" * 80)
print("STARTING JUDICIAL PROCESS VERIFICATION API")
print("=" * 80)
print()

try:
    print("1. Importing dependencies...")
    import uvicorn
    from src.entrypoints.main_api import app
    from src.core.infrastructure.config import settings
    print("   ✓ All imports successful")
    print()
    
    print("2. Configuration:")
    print(f"   Host: {settings.HOST}")
    print(f"   Port: {settings.PORT}")
    print(f"   API Title: {settings.API_TITLE}")
    print(f"   Debug: {settings.DEBUG}")
    print()
    
    print("3. Starting server...")
    print()
    
    uvicorn.run(
        app,
        host=settings.HOST,
        port=settings.PORT,
        log_level="info",
        reload=settings.DEBUG
    )
    
except KeyboardInterrupt:
    print("\n✓ Server stopped by user")
    sys.exit(0)
    
except Exception as e:
    print()
    print("=" * 80)
    print("ERROR OCCURRED:")
    print("=" * 80)
    print()
    print(f"Error Type: {type(e).__name__}")
    print(f"Error Message: {str(e)}")
    print()
    print("Full Traceback:")
    print("-" * 80)
    traceback.print_exc()
    print("-" * 80)
    print()
    sys.exit(1)

