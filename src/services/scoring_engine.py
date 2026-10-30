# src/services/scoring_engine.py
"""
Scoring Engine — Multi-parameter scoring, ranking, fairness audit.
"""
import json
from typing import List, Dict, Optional
from src.models.schemas import *
from src.config.settings import settings
from src.utils.fairness import audit_fairness


class ScoringEngine:
    def __init__(self):
        self.weights = {
            "evidence_strength": settings.WEIGHT_EVIDENCE_STRENGTH,
            "viva_performance": settings.WEIGHT_VIVA_PERFORMANCE,
            "assessment": settings.WEIGHT_ASSESSMENT,
            "consistency": settings.WEIGHT_CONSISTENCY,
        }
        self.no_github_weights = {
            "evidence_strength": settings.NO_GITHUB_WEIGHT_EVIDENCE_STRENGTH,
            "viva_performance": settings.NO_GITHUB_WEIGHT_VIVA_PERFORMANCE,
            "assessment": settings.NO_GITHUB_WEIGHT_ASSESSMENT,
            "consistency": settings.NO_GITHUB_WEIGHT_CONSISTENCY,
        }
    
    def compute_final_score(self, proof_card: ProofCard, viva_result: VivaResult) -> FinalScore:
        """Compute final multi-parameter score."""
        
        # 1. Evidence Strength (from Proof Card)
        evidence_strength = proof_card.overall_confidence
        
        # 2. Viva Performance
        viva_performance = viva_result.overall_performance * 100
        
        # 3. Assessment Score
        if proof_card.assessment_scores:
            assessment_score = sum(proof_card.assessment_scores.values()) / len(proof_card.assessment_scores)
        else:
            assessment_score = 50.0  # Neutral default
        
        # 4. Consistency
        consistency = self._compute_consistency(proof_card, viva_result)
        
        # Select weights based on GitHub presence
        has_github = any(
            any(e.type == EvidenceSource.REPO for e in s.evidence_bundle)
            for s in proof_card.unified_skills
        )
        weights = self.weights if has_github else self.no_github_weights
        
        # Weighted total
        total_score = (
            weights["evidence_strength"] * evidence_strength +
            weights["viva_performance"] * viva_performance +
            weights["assessment"] * assessment_score +
            weights["consistency"] * consistency
        )
        
        # Per-skill scores
        skill_scores = self._compute_per_skill_scores(proof_card, viva_result)
        
        # Generate human-readable reasons
        reasons = self._generate_reasons(proof_card, viva_result, skill_scores, total_score)
        
        # Pre/Post confidence
        pre_viva = {s.skill: s.final_confidence for s in proof_card.unified_skills}
        post_viva = pre_viva.copy()
        for skill, delta in viva_result.skill_deltas.items():
            post_viva[skill] = max(0, min(100, post_viva.get(skill, 50) + delta))
        
        return FinalScore(
            candidate_id=proof_card.candidate_id,
            evidence_strength=evidence_strength,
            viva_performance=viva_performance,
            assessment_score=assessment_score,
            consistency=consistency,
            total_score=total_score,
            skill_scores=skill_scores,
            reasons=reasons,
            pre_viva_confidence=pre_viva,
            post_viva_confidence=post_viva
        )
    
    def _compute_consistency(self, proof_card: ProofCard, viva_result: VivaResult) -> float:
        """Compute consistency between claimed and demonstrated skills."""
        
        consistency_scores = []
        
        for skill in proof_card.unified_skills:
            skill_name = skill.skill
            claimed_confidence = skill.final_confidence
            
            # Check viva performance for this skill
            viva_responses = [r for r in viva_result.responses if r.question.skill == skill_name]
            
            if viva_responses:
                avg_viva_score = sum(r.evaluation.score for r in viva_responses) / len(viva_responses)
                viva_confidence = avg_viva_score * 100
                
                # Consistency = how close viva matches claimed
                diff = abs(claimed_confidence - viva_confidence)
                skill_consistency = max(0, 100 - diff * 1.5)  # Penalize divergence
                consistency_scores.append(skill_consistency)
            else:
                # No viva questions for this skill - neutral
                consistency_scores.append(70)
        
        # Also check resume vs repo alignment
        for skill in proof_card.unified_skills:
            has_resume = any(e.type == EvidenceSource.RESUME for e in skill.evidence_bundle)
            has_repo = any(e.type == EvidenceSource.REPO for e in skill.evidence_bundle)
            
            if has_resume and not has_repo and skill.final_confidence > 60:
                # Claimed on resume but no repo evidence - slight penalty
                consistency_scores.append(50)
        
        return sum(consistency_scores) / len(consistency_scores) if consistency_scores else 70
    
    def _compute_per_skill_scores(self, proof_card: ProofCard, viva_result: VivaResult) -> Dict[str, Dict[str, float]]:
        """Compute per-skill breakdown."""
        skill_scores = {}
        
        for skill in proof_card.unified_skills:
            skill_name = skill.skill
            
            # Evidence component (from proof card)
            evidence = skill.final_confidence
            
            # Viva component
            viva_responses = [r for r in viva_result.responses if r.question.skill == skill_name]
            if viva_responses:
                viva = sum(r.evaluation.score for r in viva_responses) / len(viva_responses) * 100
            else:
                viva = 50  # Neutral if not tested
            
            # Assessment component
            assessment = proof_card.assessment_scores.get(skill_name, 50)
            
            # Consistency for this skill
            consistency = 100
            if viva_responses:
                diff = abs(evidence - viva)
                consistency = max(0, 100 - diff * 1.5)
            
            # Weighted total (using same weights)
            has_github = any(e.type == EvidenceSource.REPO for e in skill.evidence_bundle)
            weights = self.weights if has_github else self.no_github_weights
            
            total = (
                weights["evidence_strength"] * evidence +
                weights["viva_performance"] * viva +
                weights["assessment"] * assessment +
                weights["consistency"] * consistency
            )
            
            skill_scores[skill_name] = {
                "evidence": evidence,
                "viva": viva,
                "assessment": assessment,
                "consistency": consistency,
                "total": total
            }
        
        return skill_scores
    
    def _generate_reasons(
        self,
        proof_card: ProofCard,
        viva_result: VivaResult,
        skill_scores: Dict[str, Dict[str, float]],
        total_score: float
    ) -> List[str]:
        """Generate human-readable reasons for the score."""
        reasons = []
        
        # Top strengths
        sorted_skills = sorted(skill_scores.items(), key=lambda x: x[1]["total"], reverse=True)
        top_skills = [s for s, _ in sorted_skills[:3]]
        
        if top_skills:
            reasons.append(f"Strongest skills: {', '.join(top_skills)}")
        
        # Evidence quality
        repo_skills = [s for s in proof_card.unified_skills if any(e.type == EvidenceSource.REPO for e in s.evidence_bundle)]
        if repo_skills:
            reasons.append(f"GitHub evidence for {len(repo_skills)} skills demonstrates practical implementation")
        
        # Viva performance
        if viva_result.overall_performance > 0.75:
            reasons.append("Excellent viva performance — deep understanding confirmed")
        elif viva_result.overall_performance > 0.55:
            reasons.append("Good viva performance — solid understanding with minor gaps")
        else:
            reasons.append("Viva revealed gaps between claimed and demonstrated skills")
        
        # Tutorial clone warnings
        if proof_card.tutorial_clone_flags:
            clone_repos = [f.repo for f in proof_card.tutorial_clone_flags]
            reasons.append(f"⚠️ Tutorial clones detected in: {', '.join(clone_repos)} — evidence from these repos discounted")
        
        # Assessment alignment
        if proof_card.assessment_scores:
            high_assess = [s for s, v in proof_card.assessment_scores.items() if v > 80]
            if high_assess:
                reasons.append(f"High assessment scores in: {', '.join(high_assess)}")
        
        # Consistency
        consistent_skills = [s for s, scores in skill_scores.items() if scores["consistency"] > 80]
        inconsistent_skills = [s for s, scores in skill_scores.items() if scores["consistency"] < 50]
        
        if consistent_skills:
            reasons.append(f"Consistent claims and performance in: {', '.join(consistent_skills[:3])}")
        if inconsistent_skills:
            reasons.append(f"Inconsistencies found in: {', '.join(inconsistent_skills[:3])}")
        
        return reasons
    
    def rank_candidates(
        self,
        candidates: List[Dict],  # Each: {user_id, final_score: FinalScore}
        jd: JobDescription
    ) -> List[RankedCandidate]:
        """Rank candidates against a job description."""
        
        ranked = []
        
        for cand in candidates:
            user_id = cand["user_id"]
            final_score = cand["final_score"]
            skill_scores = final_score.skill_scores
            
            # Compute match score against JD
            match_score = 0.0
            total_weight = 0.0
            comparison = {}
            
            all_reqs = jd.required_skills + jd.preferred_skills
            
            for req in all_reqs:
                skill_name = req.skill
                weight = req.weight
                total_weight += weight
                
                candidate_score = skill_scores.get(skill_name, {}).get("total", 0)
                
                # Level mapping
                level_values = {"beginner": 30, "intermediate": 60, "advanced": 85}
                required_level = level_values.get(req.level.value, 50)
                
                # Gap assessment
                if candidate_score >= required_level:
                    gap = "none"
                elif candidate_score >= required_level * 0.75:
                    gap = "low"
                elif candidate_score >= required_level * 0.5:
                    gap = "moderate"
                else:
                    gap = "high"
                
                match_score += weight * candidate_score
                
                comparison[skill_name] = ComparisonDetail(
                    jd_required=req.level.value,
                    candidate_level=self._score_to_level(candidate_score),
                    gap=gap,
                    evidence=self._get_evidence_summary(skill_name, final_score, cand.get("proof_card"))
                )
            
            # Normalize match score
            if total_weight > 0:
                match_score = match_score / total_weight
            
            # Final ranking score: 70% match + 30% overall score
            ranking_score = 0.7 * match_score + 0.3 * final_score.total_score
            
            reasons = final_score.reasons + [
                f"JD match: {match_score:.0f}/100"
            ]
            
            ranked.append(RankedCandidate(
                candidate_id=user_id,
                score=final_score,
                rank=0,  # Will be set after sorting
                comparison=comparison,
                reasons=reasons
            ))
        
        # Sort by ranking score
        ranked.sort(key=lambda x: (0.7 * sum(c["total"] for c in x.score.skill_scores.values()) / max(len(x.score.skill_scores), 1) + 0.3 * x.score.total_score), reverse=True)
        
        # Assign ranks
        for i, rc in enumerate(ranked):
            rc.rank = i + 1
        
        return ranked
    
    def _score_to_level(self, score: float) -> str:
        """Convert numeric score to level string."""
        if score >= 80:
            return "advanced"
        elif score >= 55:
            return "intermediate"
        elif score >= 30:
            return "beginner"
        return "none"
    
    def _get_evidence_summary(self, skill: str, final_score: FinalScore, proof_card: Optional[ProofCard]) -> str:
        """Get evidence summary for a skill."""
        if not proof_card:
            return "Unknown"
        
        skill_obj = next((s for s in proof_card.unified_skills if s.skill == skill), None)
        if not skill_obj:
            return "Not claimed"
        
        sources = [e.type.value for e in skill_obj.evidence_bundle]
        return f"Sources: {', '.join(set(sources))}"


# Fairness audit function (imported from utils.fairness)
def generate_fairness_report(ranked: List[RankedCandidate], users: List[Dict]) -> Dict:
    """Generate fairness audit report."""
    return audit_fairness(ranked, users)