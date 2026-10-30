# tests/test_e2e.py
"""
End-to-end tests for ProofSkill AI.
Run with: pytest tests/test_e2e.py -v
"""
import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services.auth import AuthService
from src.services.resume_parser import ResumeParser
from src.services.evidence_synthesizer import EvidenceSynthesizer
from src.services.scoring_engine import ScoringEngine
from src.models.schemas import *
from src.db.session import init_db, db_session
from src.config.settings import settings


class TestAuthService:
    def setup_method(self):
        self.auth = AuthService()
    
    def test_password_hashing(self):
        password = "testpassword123"
        hashed = self.auth.hash_password(password)
        assert self.auth.verify_password(password, hashed)
        assert not self.auth.verify_password("wrong", hashed)
    
    def test_generate_random_password(self):
        pwd = self.auth.generate_random_password(12)
        assert len(pwd) == 12
        assert pwd.isalnum()


class TestResumeParser:
    def setup_method(self):
        self.parser = ResumeParser()
    
    def test_extract_github_urls(self):
        text = """
        Check my GitHub: https://github.com/johndoe
        Also: github.com/janedoe/project
        And: https://github.com/user/repo.git
        """
        urls = self.parser.extract_github_urls(text)
        assert len(urls) >= 2
        assert any("johndoe" in str(u) for u in urls)
    
    def test_extract_skills(self):
        text = """
        Skills: Python, JavaScript, React, Docker, PostgreSQL
        Experience with FastAPI and Django
        """
        skills = self.parser.extract_skills(text)
        skill_names = [s.name for s in skills]
        assert "Python" in skill_names
        assert "JavaScript" in skill_names
        assert "React" in skill_names
    
    def test_extract_projects(self):
        text = """
        Projects:
        - E-commerce API: Built with Python, FastAPI, PostgreSQL
        - Todo App: React, TypeScript, Redux
        """
        projects = self.parser.extract_projects(text)
        assert len(projects) >= 1
        assert any("E-commerce" in p.name for p in projects)
    
    def test_normalize_skills(self):
        skills = [
            SkillClaim(name="python", level=SkillLevel.INTERMEDIATE),
            SkillClaim(name="JavaScript", level=SkillLevel.ADVANCED),
            SkillClaim(name="react.js", level=SkillLevel.BEGINNER),
        ]
        normalized = self.parser.normalize_skills(skills)
        canon_names = [n.canonical_name for n in normalized]
        assert "Python" in canon_names
        assert "JavaScript" in canon_names
        assert "React" in canon_names


class TestEvidenceSynthesizer:
    def setup_method(self):
        self.synthesizer = EvidenceSynthesizer()
    
    def test_synthesize_no_github(self):
        resume_claims = [
            SkillClaim(name="Python", level=SkillLevel.INTERMEDIATE, source=EvidenceSource.RESUME),
            SkillClaim(name="React", level=SkillLevel.BEGINNER, source=EvidenceSource.RESUME),
        ]
        assessment_scores = {"Python": 85, "React": 60}
        
        card = self.synthesizer.synthesize_no_github(resume_claims, assessment_scores)
        
        assert card.candidate_id == ""
        assert len(card.unified_skills) == 2
        assert card.evidence_coverage == 0.0  # No repo evidence
        
        python_skill = next(s for s in card.unified_skills if s.skill == "Python")
        assert python_skill.final_confidence > 0
        assert len(python_skill.evidence_bundle) >= 2  # resume + assessment
    
    def test_synthesize_with_repo(self):
        resume_claims = [SkillClaim(name="Python", level=SkillLevel.INTERMEDIATE)]
        assessment_scores = {"Python": 80}
        
        # Mock repo analysis
        from src.models.schemas import RepoAnalysis, AuthorshipSignal, EvolutionSignal
        from src.models.schemas import TutorialCloneSignal, QualitySignal, SkillEvidence
        
        repo_analysis = RepoAnalysis(
            repo_id="test-repo",
            name="test-project",
            owner="testuser",
            authorship=AuthorshipSignal(score=0.9, total_commits=50, candidate_commits=45, primary_author=True, commit_frequency_per_week=2, time_span_days=60, email_mapping={}),
            evolution=EvolutionSignal(score=0.8, loc_growth_trend="increasing", complexity_trend="increasing", feature_commits=30, bugfix_commits=10, refactor_commits=10, first_commit_date=None, last_commit_date=None),
            tutorial_clone=TutorialCloneSignal(score=0.1, is_clone=False, confidence=0.9),
            quality=QualitySignal(score=0.85, has_tests=True, test_coverage_estimate=0.7, has_docs=True, doc_coverage=0.6, lint_score=0.9, type_hint_coverage=0.8, cyclomatic_complexity_avg=5),
            skill_evidence=[SkillEvidence(skill="Python", evidence_type="implementation", confidence=0.9, files=["main.py", "models.py"], details="Core implementation")]
        )
        
        card = self.synthesizer.synthesize(resume_claims, [repo_analysis], assessment_scores)
        
        python_skill = next(s for s in card.unified_skills if s.skill == "Python")
        assert python_skill.final_confidence > 70  # Should be high with repo evidence
        assert any(e.type == EvidenceSource.REPO for e in python_skill.evidence_bundle)
        assert card.evidence_coverage > 0


class TestScoringEngine:
    def setup_method(self):
        self.engine = ScoringEngine()
    
    def test_compute_final_score(self):
        # Create mock proof card
        proof_card = ProofCard(
            candidate_id="TEST-001",
            unified_skills=[
                UnifiedSkill(skill="Python", final_confidence=85, evidence_bundle=[
                    EvidenceItem(type=EvidenceSource.REPO, source="test-repo", detail="Implementation", weight=0.6, confidence=0.85)
                ]),
                UnifiedSkill(skill="React", final_confidence=60, evidence_bundle=[
                    EvidenceItem(type=EvidenceSource.RESUME, source="resume", detail="Claimed", weight=0.1, confidence=0.3)
                ])
            ],
            overall_confidence=72.5,
            evidence_coverage=50.0,
            assessment_scores={"Python": 85, "React": 60}
        )
        
        # Mock viva result
        viva_result = VivaResult(
            candidate_id="TEST-001",
            session_id=1,
            responses=[],
            overall_performance=0.75,
            skill_deltas={"Python": 5, "React": -2}
        )
        
        final_score = self.engine.compute_final_score(proof_card, viva_result)
        
        assert final_score.candidate_id == "TEST-001"
        assert 0 <= final_score.total_score <= 100
        assert final_score.evidence_strength == 72.5
        assert final_score.viva_performance == 75.0
        assert "Python" in final_score.skill_scores
        assert "React" in final_score.skill_scores
        assert len(final_score.reasons) > 0
    
    def test_consistency_calculation(self):
        proof_card = ProofCard(
            candidate_id="TEST-001",
            unified_skills=[
                UnifiedSkill(skill="Python", final_confidence=80, evidence_bundle=[]),
                UnifiedSkill(skill="React", final_confidence=40, evidence_bundle=[])
            ]
        )
        
        viva_result = VivaResult(
            candidate_id="TEST-001",
            session_id=1,
            responses=[
                VivaResponse(
                    question=VivaQuestion(id="q1", type=QuestionType.CODE_WALKTHROUGH, skill="Python", prompt="...", context=VivaQuestionContext()),
                    answer_text="Good answer",
                    evaluation=ResponseEvaluation(score=0.85, feedback="", signals_matched=[], signals_missed=[], confidence_delta=5),
                    response_time_ms=5000
                ),
                VivaResponse(
                    question=VivaQuestion(id="q2", type=QuestionType.KNOWLEDGE_CHECK, skill="React", prompt="...", context=VivaQuestionContext()),
                    answer_text="Weak answer",
                    evaluation=ResponseEvaluation(score=0.35, feedback="", signals_matched=[], signals_missed=[], confidence_delta=-5),
                    response_time_ms=5000
                )
            ],
            overall_performance=0.6,
            skill_deltas={"Python": 5, "React": -5}
        )
        
        consistency = self.engine._compute_consistency(proof_card, viva_result)
        
        # Python: claimed 80, viva ~85 -> consistent (high)
        # React: claimed 40, viva ~35 -> somewhat consistent
        assert 0 <= consistency <= 100


class TestFairness:
    def test_fairness_audit_pass(self):
        from src.utils.fairness import audit_fairness
        
        ranked = [
            RankedCandidate(candidate_id="C1", score=FinalScore(total_score=90), rank=1),
            RankedCandidate(candidate_id="C2", score=FinalScore(total_score=85), rank=2),
            RankedCandidate(candidate_id="C3", score=FinalScore(total_score=80), rank=3),
        ]
        
        users = [
            {"user_id": "C1", "college_tier": "tier1", "gender": "male"},
            {"user_id": "C2", "college_tier": "tier2", "gender": "female"},
            {"user_id": "C3", "college_tier": "tier3", "gender": "male"},
        ]
        
        report = audit_fairness(ranked, users)
        
        # In test, protected attributes should have 0 importance
        assert report.passed == True  # Should pass with mock data
        assert all(v == 0.0 for v in report.feature_importance.values())


# Integration test (requires full setup)
@pytest.mark.integration
def test_full_flow():
    """Test complete flow from login to results."""
    # This would require:
    # 1. Database with test data
    # 2. Mock GitHub API
    # 3. Mock model
    # 4. Mock voice pipeline
    pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])