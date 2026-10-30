#!/usr/bin/env python
"""Reset database and create sample users"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.db.session import init_db, engine
from src.services.auth import AuthService
from pathlib import Path
from sqlalchemy import text

def main():
    print("🔄 Resetting database...")
    
    # Drop all tables - handle gracefully if they don't exist
    tables = ['users', 'resumes', 'github_links', 'selected_repos', 
              'repo_analyses', 'proof_cards', 'viva_sessions', 
              'viva_responses', 'final_scores', 'recruiter_jds', 
              'rankings', 'imats_sync']
    
    with engine.connect() as conn:
        for table in tables:
            try:
                conn.execute(text(f'DROP TABLE IF EXISTS {table}'))
            except:
                pass  # Table doesn't exist, ignore
        conn.commit()
    
    print("✅ Tables dropped (or didn't exist)")
    
    # Recreate tables
    init_db()
    print("✅ Tables recreated")
    
    # Create sample users
    auth = AuthService()
    resume_dir = Path("data/resumes")
    resume_files = sorted(list(resume_dir.glob("*.pdf")) + list(resume_dir.glob("*.docx")))
    
    print(f"\n📄 Found {len(resume_files)} resume files:")
    for f in resume_files:
        print(f"  - {f.name}")
    
    print("\n👥 Creating sample users:")
    print("=" * 60)
    
    for i, resume_file in enumerate(resume_files, 1):
        user_id = f"CAND-{i:04d}"
        password = auth.generate_random_password()
        auth.setup_candidate_credentials(user_id, resume_file.name, password)
        print(f"  {user_id} : {password}")
    
    print("\n✅ All done!")

if __name__ == "__main__":
    main()