# src/config/settings.py
"""
Configuration management using Pydantic Settings.
Loads from .env file and environment variables.
"""
from pathlib import Path
from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ============================================================
    # APP SETTINGS
    # ============================================================
    APP_NAME: str = "ProofSkill AI"
    DEBUG: bool = True
    SECRET_KEY: str = Field(
        default="proofskill-development-secret-change-in-production",
        min_length=32,
    )
    RECRUITER_ID: str = "admin"
    RECRUITER_PASSWORD: str = "password"
    CANDIDATE_DEFAULT_PASSWORD: str = "password"

    # ============================================================
    # DATABASE
    # ============================================================
    DATABASE_URL: str = "sqlite:///data/proofskill.db"

    # ============================================================
    # GITHUB API
    # ============================================================
    GITHUB_TOKEN: str = ""
    GITHUB_API_BASE: str = "https://api.github.com"
    GITHUB_RATE_LIMIT: int = 5000

    # ============================================================
    # ELEVENLABS TTS
    # ============================================================
    ELEVENLABS_API_KEY: str = ""
    ELEVENLABS_VOICE_ID: str = "21m00Tcm4TlvDq8ikWAM"

    # ============================================================
    # WHISPER STT
    # ============================================================
    WHISPER_MODEL: str = "large-v3"
    WHISPER_DEVICE: str = "cuda"
    WHISPER_COMPUTE_TYPE: str = "float16"
    WHISPER_API_URL: str = "https://unhelpful-corny-jumbo.ngrok-free.dev/transcribe"
    WHISPER_API_TIMEOUT: int = 120

    # ============================================================
    # GRADIO TTS (Your Audio8-TTS Model)
    # ============================================================
    GRADIO_TTS_URL: str = "https://bd512e52f4484d878a.gradio.live/"
    GRADIO_TTS_API_NAME: str = "/predict"
    GRADIO_TTS_TIMEOUT: int = 120

    # ============================================================
    # FINE-TUNED MODEL
    # ============================================================
    MODEL_PATH: Path = Path("models/fine_tuned/")
    MODEL_BACKEND: str = "auto"
    MODEL_API_URL: str = ""
    MODEL_API_KEY: str = ""
    MODEL_API_TIMEOUT: int = 120
    MODEL_GENERATION_MAX_TOKENS: int = 1024
    MODEL_DEVICE: str = "cuda"
    MODEL_MAX_LENGTH: int = 4096
    MODEL_N_GPU_LAYERS: int = -1
    MODEL_N_BATCH: int = 512

    # ============================================================
    # IMATS SANDBOX
    # ============================================================
    IMATS_API_URL: str = ""
    IMATS_API_KEY: str = ""

    # ============================================================
    # FILE PATHS
    # ============================================================
    RESUME_DIR: Path = Path("data/resumes")
    REPO_CACHE_DIR: Path = Path("data/repo_cache")
    EXPORT_DIR: Path = Path("data/exports")

    # ============================================================
    # FAIRNESS
    # ============================================================
    PROTECTED_ATTRIBUTES: List[str] = ["college", "gender", "age", "location"]

    # ============================================================
    # SCORING WEIGHTS
    # ============================================================
    WEIGHT_EVIDENCE_STRENGTH: float = 0.35
    WEIGHT_VIVA_PERFORMANCE: float = 0.35
    WEIGHT_ASSESSMENT: float = 0.20
    WEIGHT_CONSISTENCY: float = 0.10

    NO_GITHUB_WEIGHT_EVIDENCE_STRENGTH: float = 0.20
    NO_GITHUB_WEIGHT_VIVA_PERFORMANCE: float = 0.50
    NO_GITHUB_WEIGHT_ASSESSMENT: float = 0.25
    NO_GITHUB_WEIGHT_CONSISTENCY: float = 0.05

    # ============================================================
    # VIVA SETTINGS
    # ============================================================
    VIVA_MAX_QUESTIONS: int = 10
    VIVA_ANSWER_TIMEOUT_SECONDS: int = 60
    VIVA_INTRO_DURATION_SECONDS: int = 30

    # ============================================================
    # REPO ANALYSIS
    # ============================================================
    MAX_REPO_SIZE_MB: int = 500
    MAX_FILE_SIZE_MB: int = 1
    ANALYSIS_TIMEOUT_SECONDS: int = 300
    TUTORIAL_CLONE_THRESHOLD: float = 0.6

    # ============================================================
    # LOGGING
    # ============================================================
    LOG_LEVEL: str = "INFO"
    LOG_FILE: Path = Path("logs/proofskill.log")


# Singleton instance
settings = Settings()

# Ensure directories exist
for path in [
    settings.RESUME_DIR,
    settings.REPO_CACHE_DIR,
    settings.EXPORT_DIR,
    settings.LOG_FILE.parent,
    settings.MODEL_PATH,
]:
    path.mkdir(parents=True, exist_ok=True)