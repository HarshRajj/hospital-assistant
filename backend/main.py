"""Main entrypoint for hospital assistant backend services."""
import sys
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))


def main():
    """Main entrypoint - can be used for CLI commands or utilities."""
    print("🏥 Hospital Assistant Backend")
    print("=" * 50)
    print("\nAvailable services:")
    print("  - API Server: python -m api.server")
    print("  - Voice Agent: python -m voice-agent.agent")
    print("\nFor deployment:")
    print("  - API: uvicorn api.server:app --host 0.0.0.0 --port 8000")
    print("  - Agent: python voice-agent/agent.py")
    print("\nConfiguration: backend/.env")
    print("=" * 50)


if __name__ == "__main__":
    main()

