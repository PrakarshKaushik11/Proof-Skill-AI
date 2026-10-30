#!/usr/bin/env python
"""Test login credentials"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services.auth import AuthService

def main():
    auth = AuthService()
    test_creds = [
        ('CAND-0042', 'xK9mP2qR'),
        ('CAND-0117', 'vL8nB4wT'),
        ('CAND-0293', 'pQ3rM7zX'),
    ]
    
    print("Testing login credentials:")
    print("=" * 40)
    
    for uid, pwd in test_creds:
        user = auth.validate_credentials(uid, pwd)
        status = "✅ PASS" if user else "❌ FAIL"
        print(f"  {uid}: {status}")
    
    print("\nAll credentials tested!")

if __name__ == "__main__":
    main()