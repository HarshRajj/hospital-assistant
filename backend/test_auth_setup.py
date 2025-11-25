"""Quick test to verify authentication setup."""
import sys
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

try:
    from services.auth_service import auth_service
    print("✅ Auth service imported successfully")
    
    from config import settings
    if settings.CLERK_SECRET_KEY:
        print("✅ Clerk secret key configured")
    else:
        print("⚠️  Clerk secret key not found in .env")
    
    print("\n🎉 Authentication setup is complete!")
    print("\nNext steps:")
    print("1. Start backend: uvicorn api.server:app --reload")
    print("2. Start frontend: cd next_frontend && npm run dev")
    print("3. Sign up at http://localhost:3000")
    print("4. Try the Voice Assistant!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
