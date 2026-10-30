#!/usr/bin/env python
"""
Database initialization script.
Run with: python src/db/init_db.py
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.db.session import init_db
from src.config.settings import settings


def main():
    print(f"Initializing database: {settings.DATABASE_URL}")
    print(f"Resume directory: {settings.RESUME_DIR}")
    print(f"Repo cache directory: {settings.REPO_CACHE_DIR}")
    print(f"Export directory: {settings.EXPORT_DIR}")
    
    try:
        init_db()
        print("✅ Database initialized successfully!")
    except Exception as e:
        print(f"❌ Failed to initialize database: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()