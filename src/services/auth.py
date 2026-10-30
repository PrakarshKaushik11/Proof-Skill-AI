# src/services/auth.py
"""
Authentication Service — Random credential validation, JWT sessions.
"""
import bcrypt
import jwt
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy import text
from src.db.session import db_session
from src.config.settings import settings
from src.models.schemas import User


class AuthService:
    def __init__(self):
        self.secret_key = settings.SECRET_KEY
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 15
        self.refresh_token_expire_days = 7
    
    def hash_password(self, password: str) -> str:
        """Hash password with bcrypt."""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against hash."""
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    
    def validate_credentials(self, user_id: str, password: str) -> Optional[User]:
        """Validate user credentials against database."""
        with db_session() as db:
            result = db.execute(
                text("SELECT * FROM users WHERE user_id = :uid"),
                {"uid": user_id.upper()}
            ).fetchone()
            
            if not result:
                return None
            
            if not self.verify_password(password, result.password_hash):
                return None
            
            return User(
                user_id=result.user_id,
                password_hash=result.password_hash,
                resume_path=result.resume_path,
                candidate_name=getattr(result, "candidate_name", "Candidate"),
                consent_given=bool(result.consent_given),
                created_at=result.created_at,
                updated_at=result.updated_at
            )
    
    def create_access_token(self, user_id: str) -> str:
        """Create JWT access token."""
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        payload = {"sub": user_id, "exp": expire, "type": "access"}
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def create_refresh_token(self, user_id: str) -> str:
        """Create JWT refresh token."""
        expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        payload = {"sub": user_id, "exp": expire, "type": "refresh"}
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str) -> Optional[str]:
        """Verify JWT token and return user_id."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            if payload.get("type") == "access":
                return payload.get("sub")
        except jwt.PyJWTError:
            pass
        return None
    
    def refresh_access_token(self, refresh_token: str) -> Optional[str]:
        """Create new access token from refresh token."""
        try:
            payload = jwt.decode(refresh_token, self.secret_key, algorithms=[self.algorithm])
            if payload.get("type") == "refresh":
                user_id = payload.get("sub")
                return self.create_access_token(user_id)
        except jwt.PyJWTError:
            pass
        return None
    
    def generate_random_password(self, length: int = 12) -> str:
        """Generate random alphanumeric password."""
        import secrets
        import string
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    def validate_recruiter_credentials(self, recruiter_id: str, password: str) -> bool:
        """Validate the configured recruiter/admin account."""
        return (
            recruiter_id.strip().lower() == settings.RECRUITER_ID.lower()
            and password == settings.RECRUITER_PASSWORD
        )

    def setup_candidate_credentials(
        self,
        user_id: str,
        resume_path: str,
        password: str = None,
        candidate_name: str = "Candidate",
    ) -> str:
        """Create or update candidate credentials in database."""
        if password is None:
            password = self.generate_random_password()
        
        password_hash = self.hash_password(password)
        
        with db_session() as db:
            db.execute(text("""
                INSERT OR REPLACE INTO users
                    (user_id, password_hash, resume_path, candidate_name, consent_given)
                VALUES (:uid, :hash, :resume, :candidate_name, 0)
            """), {
                "uid": user_id,
                "hash": password_hash,
                "resume": resume_path,
                "candidate_name": candidate_name,
            })
            db.commit()
        
        return password


# Pre-generate credentials for 400 candidates (run once)
def pregenerate_credentials(resume_dir: str = "data/resumes") -> list:
    """Generate credentials for all resume files in directory."""
    import os
    from pathlib import Path
    
    auth = AuthService()
    credentials = []
    
    resume_files = sorted(Path(resume_dir).glob("*.pdf")) + sorted(Path(resume_dir).glob("*.docx"))
    
    for i, resume_file in enumerate(resume_files, 1):
        user_id = f"CAND-{i:04d}"
        password = auth.generate_random_password()
        auth.setup_candidate_credentials(user_id, resume_file.name, password)
        credentials.append({"user_id": user_id, "password": password, "resume": resume_file.name})
    
    return credentials