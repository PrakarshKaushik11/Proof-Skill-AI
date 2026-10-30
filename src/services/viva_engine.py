# src/services/viva_engine.py
"""
Viva Engine — Generate questions from Proof Card, evaluate responses.
"""
import json
from typing import List, Dict, Optional
from src.services.model_client import FineTunedModel
from src.models.schemas import *
from src.config.settings import settings


class VivaEngine:
    def __init__(self):
        self.model = FineTunedModel()
        self.question_templates = self._load_question_templates()
    
    def _load_question_templates(self) -> dict:
        """Load question generation templates."""
        return {
            QuestionType.CODE_WALKTHROUGH: {
                "prompt": "Generate a code walkthrough question for skill '{skill}' based on the candidate's repository '{repo}' file '{file}'. "
                         "The question should ask them to explain a specific function or module. "
                         "Include the relevant code snippet in context.",
                "expected_signals": ["architecture", "data_flow", "design_decisions", "error_handling", "scalability"]
            },
            QuestionType.ALTERNATIVE_APPROACH: {
                "prompt": "Generate an 'alternative approach' question for skill '{skill}' based on the candidate's code in '{repo}'. "
                         "Identify a specific implementation choice they made and ask why they didn't use an alternative. "
                         "Include the code snippet showing their choice.",
                "expected_signals": ["trade_offs", "constraints", "team_context", "learning"]
            },
            QuestionType.DEBUG: {
                "prompt": "Generate a debugging question for skill '{skill}' based on the candidate's code in '{repo}'. "
                         "Create a realistic bug scenario (off-by-one, null pointer, race condition, SQL injection, etc.) "
                         "and provide the buggy code snippet. Ask them to identify and fix the bug.",
                "expected_signals": ["bug_identification", "root_cause", "fix", "test_case", "prevention"]
            },
            QuestionType.EXTEND_FEATURE: {
                "prompt": "Generate a feature extension question for skill '{skill}' based on the candidate's code in '{repo}'. "
                         "Ask them to add a new feature (pagination, caching, authentication, logging, etc.) to an existing module. "
                         "Provide context about the existing code structure.",
                "expected_signals": ["design", "implementation_plan", "testing", "integration", "edge_cases"]
            },
            QuestionType.BEHAVIORAL: {
                "prompt": "Generate a behavioral (STAR format) question for a fresher candidate assessing '{skill}'. "
                         "Focus on situations relevant to entry-level roles: team projects, learning new tech, debugging, conflicts.",
                "expected_signals": ["situation", "task", "action", "result", "reflection"]
            },
            QuestionType.KNOWLEDGE_CHECK: {
                "prompt": "Generate a conceptual knowledge check question for '{skill}' appropriate for a fresher. "
                         "Test understanding of core concepts, not just definitions.",
                "expected_signals": ["conceptual_understanding", "practical_implications", "common_pitfalls"]
            }
        }
    
    def generate_questions(self, proof_card: ProofCard) -> List[VivaQuestion]:
        """Generate personalized viva questions from Proof Card."""
        
        # Build context for model
        context = self._build_model_context(proof_card)
        
        # Generate questions using fine-tuned model
        questions = self.model.generate_questions(context, settings.VIVA_MAX_QUESTIONS)
        
        # Ensure we have the right distribution
        questions = self._balance_question_types(questions, proof_card)
        
        # Assign IDs
        for i, q in enumerate(questions):
            q.id = f"q{i+1}"
        
        return questions[:settings.VIVA_MAX_QUESTIONS]
    
    def _build_model_context(self, proof_card: ProofCard) -> dict:
        """Build context object for question generation."""
        # Extract repo details for technical questions
        repo_details = []
        for skill in proof_card.unified_skills:
            for evidence in skill.evidence_bundle:
                if evidence.type == EvidenceSource.REPO:
                    repo_details.append({
                        "repo": evidence.source,
                        "skill": skill.skill,
                        "evidence_type": evidence.detail,
                        "confidence": evidence.confidence
                    })
        
        return {
            "candidate_id": proof_card.candidate_id,
            "skills": [
                {
                    "skill": s.skill,
                    "confidence": s.final_confidence,
                    "has_repo_evidence": any(e.type == EvidenceSource.REPO for e in s.evidence_bundle),
                    "has_assessment": any(e.type == EvidenceSource.ASSESSMENT for e in s.evidence_bundle),
                    "tutorial_clone_flag": s.tutorial_clone_flag,
                    "gap_notes": s.gap_notes
                }
                for s in proof_card.unified_skills
            ],
            "repo_details": repo_details,
            "tutorial_clone_flags": [
                {"repo": f.repo, "type": f.clone_type, "confidence": f.confidence}
                for f in proof_card.tutorial_clone_flags
            ]
        }
    
    def _balance_question_types(self, questions: List[VivaQuestion], proof_card: ProofCard) -> List[VivaQuestion]:
        """Ensure good distribution of question types."""
        # Count questions by type
        type_counts = {}
        for q in questions:
            type_counts[q.type] = type_counts.get(q.type, 0) + 1
        
        # Target distribution
        has_github = any(
            any(e.type == EvidenceSource.REPO for e in s.evidence_bundle)
            for s in proof_card.unified_skills
        )
        
        if has_github:
            targets = {
                QuestionType.CODE_WALKTHROUGH: 3,
                QuestionType.ALTERNATIVE_APPROACH: 2,
                QuestionType.DEBUG: 1,
                QuestionType.EXTEND_FEATURE: 1,
                QuestionType.BEHAVIORAL: 2,
                QuestionType.KNOWLEDGE_CHECK: 1,
            }
        else:
            targets = {
                QuestionType.CODE_WALKTHROUGH: 0,
                QuestionType.ALTERNATIVE_APPROACH: 0,
                QuestionType.DEBUG: 0,
                QuestionType.EXTEND_FEATURE: 0,
                QuestionType.BEHAVIORAL: 3,
                QuestionType.KNOWLEDGE_CHECK: 2,
            }
        
        # If model didn't generate balanced set, we could re-generate or adjust
        # For now, return as-is (model should be trained to balance)
        return questions
    
    def evaluate_response(self, question: VivaQuestion, answer: str) -> ResponseEvaluation:
        """Evaluate candidate's answer to a viva question."""
        
        # Use fine-tuned model for evaluation
        evaluation = self.model.evaluate_response(question, answer)
        
        return evaluation
    
    def run_session(self, proof_card: ProofCard, mode: VoiceMode = VoiceMode.HYBRID) -> VivaResult:
        """Run complete viva session (used for batch/testing)."""
        questions = self.generate_questions(proof_card)
        responses = []
        
        for question in questions:
            # In real app, this would be interactive
            # For batch, we'd need pre-recorded answers
            pass
        
        # Calculate overall performance
        if responses:
            overall = sum(r.evaluation.score for r in responses) / len(responses)
        else:
            overall = 0.0
        
        # Skill deltas
        skill_deltas = {}
        for r in responses:
            skill = r.question.skill
            if skill not in skill_deltas:
                skill_deltas[skill] = 0.0
            skill_deltas[skill] += r.evaluation.confidence_delta
        
        return VivaResult(
            candidate_id=proof_card.candidate_id,
            session_id=0,
            responses=responses,
            overall_performance=overall,
            skill_deltas=skill_deltas
        )


# Convenience functions for direct use
def create_code_walkthrough_question(skill: str, repo: str, file: str, code_snippet: str, function: str) -> VivaQuestion:
    """Create a code walkthrough question manually."""
    return VivaQuestion(
        id="",
        type=QuestionType.CODE_WALKTHROUGH,
        skill=skill,
        prompt=f"In your {repo} repository, walk me through the {function} function in {file}. How does it work?",
        context=VivaQuestionContext(
            repo=repo,
            file=file,
            code_snippet=code_snippet,
            function=function
        ),
        expected_signals=["architecture", "data_flow", "design_decisions", "error_handling"]
    )


def create_alternative_approach_question(skill: str, repo: str, file: str, code_snippet: str, 
                                         their_choice: str, alternative: str) -> VivaQuestion:
    """Create an alternative approach question."""
    return VivaQuestion(
        id="",
        type=QuestionType.ALTERNATIVE_APPROACH,
        skill=skill,
        prompt=f"In {repo}/{file}, you used {their_choice}. Why did you choose this over {alternative}? What are the trade-offs?",
        context=VivaQuestionContext(
            repo=repo,
            file=file,
            code_snippet=code_snippet
        ),
        expected_signals=["trade_offs", "constraints", "performance", "maintainability"]
    )


def create_debug_question(skill: str, repo: str, file: str, buggy_code: str, bug_type: str) -> VivaQuestion:
    """Create a debugging question."""
    return VivaQuestion(
        id="",
        type=QuestionType.DEBUG,
        skill=skill,
        prompt=f"This code from your {repo} repository has a {bug_type} bug. Can you identify and fix it?",
        context=VivaQuestionContext(
            repo=repo,
            file=file,
            code_snippet=buggy_code
        ),
        expected_signals=["bug_identification", "root_cause", "fix", "test_case"]
    )


def create_behavioral_question(skill: str, scenario: str) -> VivaQuestion:
    """Create a behavioral question."""
    return VivaQuestion(
        id="",
        type=QuestionType.BEHAVIORAL,
        skill=skill,
        prompt=scenario,
        context=VivaQuestionContext(scenario=scenario),
        expected_signals=["situation", "task", "action", "result", "reflection"]
    )