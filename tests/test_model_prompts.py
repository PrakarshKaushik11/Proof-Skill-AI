# tests/test_model_prompts.py
"""
Tests for model prompt outputs.
Run with: pytest tests/test_model_prompts.py -v
"""
import pytest
import json
from src.services.model_client import FineTunedModel
from src.models.schemas import *


class TestModelPrompts:
    def setup_method(self):
        self.model = FineTunedModel()
    
    def test_question_generation_structure(self):
        """Test that generated questions have correct structure."""
        context = {
            "skills": [
                {"skill": "Python", "confidence": 85, "has_repo_evidence": True, "tutorial_clone_flag": False},
                {"skill": "React", "confidence": 60, "has_repo_evidence": False, "tutorial_clone_flag": False}
            ],
            "repo_details": [
                {"repo": "ecommerce-api", "skill": "Python", "evidence_type": "implementation", "confidence": 0.9}
            ],
            "tutorial_clone_flags": []
        }
        
        questions = self.model.generate_questions(context, max_questions=5)
        
        assert len(questions) >= 1
        
        for q in questions:
            # Check required fields
            assert q.id is not None
            assert q.type in QuestionType
            assert q.skill is not None
            assert q.prompt is not None
            assert isinstance(q.context, VivaQuestionContext)
            assert isinstance(q.expected_signals, list)
            assert 1 <= q.difficulty <= 5
    
    def test_technical_questions_have_repo_context(self):
        """Technical questions must reference candidate's actual code."""
        context = {
            "skills": [
                {"skill": "Python", "confidence": 85, "has_repo_evidence": True, "tutorial_clone_flag": False}
            ],
            "repo_details": [
                {"repo": "ecommerce-api", "skill": "Python", "evidence_type": "implementation", "confidence": 0.9}
            ],
            "tutorial_clone_flags": []
        }
        
        questions = self.model.generate_questions(context, max_questions=5)
        
        technical_types = {
            QuestionType.CODE_WALKTHROUGH,
            QuestionType.ALTERNATIVE_APPROACH,
            QuestionType.DEBUG,
            QuestionType.EXTEND_FEATURE
        }
        
        for q in questions:
            if q.type in technical_types:
                # Must have repo context
                assert q.context.repo is not None, f"Technical question {q.id} missing repo context"
                assert q.context.code_snippet is not None, f"Technical question {q.id} missing code snippet"
    
    def test_no_generic_questions(self):
        """Verify no generic questions like 'What is OOP?' are generated."""
        context = {
            "skills": [{"skill": "Python", "confidence": 50, "has_repo_evidence": False}],
            "repo_details": [],
            "tutorial_clone_flags": []
        }
        
        questions = self.model.generate_questions(context, max_questions=5)
        
        generic_phrases = [
            "what is", "define", "explain the concept", "difference between",
            "advantages of", "disadvantages of", "features of"
        ]
        
        for q in questions:
            prompt_lower = q.prompt.lower()
            # Allow these in behavioral/knowledge contexts but not as standalone
            if q.type == QuestionType.KNOWLEDGE_CHECK:
                # Knowledge checks can have "what is" but should be specific
                assert len(q.prompt) > 30, f"Knowledge check too short: {q.prompt}"
            else:
                for phrase in generic_phrases:
                    # Should not be the main question
                    assert not prompt_lower.strip().startswith(phrase), \
                        f"Question appears generic: {q.prompt}"
    
    def test_question_distribution(self):
        """Test that question types are appropriately distributed."""
        context = {
            "skills": [
                {"skill": "Python", "confidence": 85, "has_repo_evidence": True, "tutorial_clone_flag": False},
                {"skill": "React", "confidence": 60, "has_repo_evidence": True, "tutorial_clone_flag": False},
                {"skill": "Problem Solving", "confidence": 70, "has_repo_evidence": False, "tutorial_clone_flag": False}
            ],
            "repo_details": [
                {"repo": "backend-api", "skill": "Python", "evidence_type": "implementation", "confidence": 0.9},
                {"repo": "frontend-app", "skill": "React", "evidence_type": "framework_usage", "confidence": 0.8}
            ],
            "tutorial_clone_flags": []
        }
        
        questions = self.model.generate_questions(context, max_questions=10)
        
        type_counts = {}
        for q in questions:
            type_counts[q.type] = type_counts.get(q.type, 0) + 1
        
        # Should have at least some technical questions (since repo evidence exists)
        technical_count = sum(
            type_counts.get(t, 0) for t in [
                QuestionType.CODE_WALKTHROUGH,
                QuestionType.ALTERNATIVE_APPROACH,
                QuestionType.DEBUG,
                QuestionType.EXTEND_FEATURE
            ]
        )
        assert technical_count >= 2, f"Expected at least 2 technical questions, got {technical_count}"
        
        # Should have behavioral questions
        assert type_counts.get(QuestionType.BEHAVIORAL, 0) >= 1, "Missing behavioral questions"
    
    def test_evaluation_output_structure(self):
        """Test response evaluation output structure."""
        question = VivaQuestion(
            id="q1",
            type=QuestionType.CODE_WALKTHROUGH,
            skill="Python",
            prompt="Walk me through the auth flow",
            context=VivaQuestionContext(
                repo="ecommerce-api",
                file="api/auth.py",
                code_snippet="def verify_token(token): ...",
                function="verify_token"
            ),
            expected_signals=["JWT validation", "error handling", "token refresh"]
        )
        
        answer = "The verify_token function uses PyJWT to decode the token with HS256 algorithm. It catches ExpiredSignatureError and InvalidTokenError exceptions and raises custom AuthError."
        
        evaluation = self.model.evaluate_response(question, answer)
        
        # Check structure
        assert 0 <= evaluation.score <= 1
        assert isinstance(evaluation.feedback, str)
        assert len(evaluation.feedback) > 10
        assert isinstance(evaluation.signals_matched, list)
        assert isinstance(evaluation.signals_missed, list)
        assert -20 <= evaluation.confidence_delta <= 20
    
    def test_evaluation_consistency(self):
        """Same answer should get similar scores."""
        question = VivaQuestion(
            id="q1", type=QuestionType.KNOWLEDGE_CHECK, skill="Python",
            prompt="What is a decorator in Python?",
            context=VivaQuestionContext(),
            expected_signals=["function wrapper", "syntax @decorator", "use cases"]
        )
        
        answer = "A decorator is a function that takes another function and extends its behavior without modifying it. It uses the @decorator syntax."
        
        scores = []
        for _ in range(3):
            eval_result = self.model.evaluate_response(question, answer)
            scores.append(eval_result.score)
        
        # Scores should be consistent (low variance)
        import statistics
        if len(scores) > 1:
            stdev = statistics.stdev(scores)
            assert stdev < 0.15, f"Evaluation inconsistent: scores={scores}, stdev={stdev}"


def test_mock_model_outputs():
    """Test mock model outputs for development."""
    model = FineTunedModel()
    model.model_type = "mock"
    
    # Test question generation
    questions = model.generate_questions({
        "skills": [{"skill": "Python", "confidence": 80, "has_repo_evidence": True}],
        "repo_details": [{"repo": "test", "skill": "Python", "evidence_type": "implementation", "confidence": 0.9}],
        "tutorial_clone_flags": []
    }, max_questions=5)
    
    assert len(questions) >= 2
    assert all(isinstance(q, VivaQuestion) for q in questions)
    
    # Test evaluation
    question = VivaQuestion(
        id="q1", type=QuestionType.CODE_WALKTHROUGH, skill="Python",
        prompt="Test question", context=VivaQuestionContext(),
        expected_signals=["signal1"]
    )
    
    eval_result = model.evaluate_response(question, "Test answer")
    
    assert isinstance(eval_result, ResponseEvaluation)
    assert 0 <= eval_result.score <= 1
    assert -20 <= eval_result.confidence_delta <= 20


if __name__ == "__main__":
    pytest.main([__file__, "-v"])