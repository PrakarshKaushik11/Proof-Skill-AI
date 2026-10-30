# src/services/evidence_synthesizer.py
"""
Evidence Synthesizer — Combine resume, repo, assessment into Proof Card.
"""
import json
from typing import List, Dict, Optional
from src.models.schemas import *
from src.config.settings import settings


class EvidenceSynthesizer:
    def __init__(self):
        # Evidence weights for confidence calculation
        self.weights = {
            EvidenceSource.REPO: 0.60,
            EvidenceSource.ASSESSMENT: 0.30,
            EvidenceSource.RESUME: 0.10,
            EvidenceSource.VIVA: 0.20,  # Added later during viva
        }
    
    def synthesize(
        self,
        resume_claims: List[SkillClaim],
        repo_analyses: List[RepoAnalysis],
        assessment_scores: Dict[str, float]
    ) -> ProofCard:
        """Synthesize all evidence into a unified Proof Card."""
        
        # Collect all unique skills from all sources
        all_skills = set()
        
        # From resume
        for claim in resume_claims:
            all_skills.add(claim.name)
        
        # From repo analyses
        for analysis in repo_analyses:
            for evidence in analysis.skill_evidence:
                all_skills.add(evidence.skill)
        
        # From assessments
        for skill in assessment_scores:
            all_skills.add(skill)
        
        # Build unified skills
        unified_skills = []
        tutorial_clone_flags = []
        
        for skill in sorted(all_skills):
            unified = self._synthesize_skill(
                skill, resume_claims, repo_analyses, assessment_scores
            )
            unified_skills.append(unified)
            
            # Check for tutorial clone flags related to this skill
            for analysis in repo_analyses:
                if analysis.tutorial_clone.is_clone:
                    for evidence in analysis.skill_evidence:
                        if evidence.skill == skill:
                            tutorial_clone_flags.append(CloneFlag(
                                repo=analysis.name,
                                clone_type=analysis.tutorial_clone.clone_type or "unknown",
                                confidence=analysis.tutorial_clone.confidence,
                                explanation=f"Repository '{analysis.name}' detected as {analysis.tutorial_clone.clone_type} tutorial clone. "
                                           f"Skill '{skill}' evidence from this repo may be inflated."
                            ))
                            break
        
        # Calculate overall metrics
        overall_confidence = sum(s.final_confidence for s in unified_skills) / len(unified_skills) if unified_skills else 0
        evidence_coverage = sum(1 for s in unified_skills if any(e.type == EvidenceSource.REPO for e in s.evidence_bundle)) / len(unified_skills) * 100 if unified_skills else 0
        
        return ProofCard(
            candidate_id="",  # Set by caller
            unified_skills=unified_skills,
            tutorial_clone_flags=tutorial_clone_flags,
            assessment_scores=assessment_scores,
            overall_confidence=overall_confidence,
            evidence_coverage=evidence_coverage
        )
    
    def _synthesize_skill(
        self,
        skill: str,
        resume_claims: List[SkillClaim],
        repo_analyses: List[RepoAnalysis],
        assessment_scores: Dict[str, float]
    ) -> UnifiedSkill:
        """Synthesize evidence for a single skill."""
        
        evidence_bundle = []
        repo_evidence_strength = 0.0
        has_repo_evidence = False
        tutorial_clone_flag = False
        
        # 1. Resume claim
        resume_claim = next((c for c in resume_claims if c.name == skill), None)
        if resume_claim:
            level_weight = {"beginner": 0.3, "intermediate": 0.6, "advanced": 0.9}.get(resume_claim.level.value, 0.3)
            evidence_bundle.append(EvidenceItem(
                type=EvidenceSource.RESUME,
                source="resume",
                detail=f"Claimed as {resume_claim.level.value} in resume",
                weight=self.weights[EvidenceSource.RESUME] * level_weight,
                confidence=level_weight * 0.5  # Resume claims are weak evidence
            ))
        
        # 2. Repository evidence
        repo_evidences = []
        for analysis in repo_analyses:
            for evidence in analysis.skill_evidence:
                if evidence.skill == skill:
                    repo_evidences.append((analysis, evidence))
        
        if repo_evidences:
            has_repo_evidence = True
            # Check if any repo is a tutorial clone
            for analysis, evidence in repo_evidences:
                if analysis.tutorial_clone.is_clone:
                    tutorial_clone_flag = True
            
            # Calculate repo evidence strength
            for analysis, evidence in repo_evidences:
                # Weight by authorship and quality
                authorship_weight = analysis.authorship.score if analysis.authorship.primary_author else 0.5
                quality_weight = analysis.quality.score
                clone_penalty = 0.5 if analysis.tutorial_clone.is_clone else 1.0
                
                effective_weight = self.weights[EvidenceSource.REPO] * authorship_weight * quality_weight * clone_penalty
                # Quality affects the amount of evidence contributed; the
                # observed implementation confidence remains tied to the
                # evidence and authorship rather than being penalized twice.
                effective_confidence = evidence.confidence * authorship_weight * clone_penalty
                
                repo_evidence_strength = max(repo_evidence_strength, effective_confidence)
                
                evidence_bundle.append(EvidenceItem(
                    type=EvidenceSource.REPO,
                    source=analysis.name,
                    detail=f"{evidence.evidence_type} in {', '.join(evidence.files[:3])}",
                    weight=effective_weight,
                    confidence=effective_confidence
                ))
        
        # 3. Assessment scores
        if skill in assessment_scores:
            score = assessment_scores[skill]  # 0-100
            norm_score = score / 100.0
            evidence_bundle.append(EvidenceItem(
                type=EvidenceSource.ASSESSMENT,
                source="assessment",
                detail=f"Assessment score: {score:.0f}/100",
                weight=self.weights[EvidenceSource.ASSESSMENT] * norm_score,
                confidence=norm_score
            ))
        
        # Calculate final confidence (0-100)
        total_weight = sum(e.weight for e in evidence_bundle)
        if total_weight > 0:
            weighted_confidence = sum(e.confidence * e.weight for e in evidence_bundle) / total_weight
        else:
            weighted_confidence = 0.0
        
        final_confidence = min(weighted_confidence * 100, 100)
        
        # Generate gap notes
        gap_notes = self._generate_gap_notes(skill, final_confidence, has_repo_evidence, resume_claim, assessment_scores)
        
        return UnifiedSkill(
            skill=skill,
            final_confidence=final_confidence,
            evidence_bundle=evidence_bundle,
            tutorial_clone_flag=tutorial_clone_flag,
            gap_notes=gap_notes
        )
    
    def _generate_gap_notes(
        self,
        skill: str,
        confidence: float,
        has_repo_evidence: bool,
        resume_claim: Optional[SkillClaim],
        assessment_scores: Dict[str, float]
    ) -> Optional[str]:
        """Generate actionable gap notes."""
        notes = []
        
        if confidence < 40:
            notes.append(f"Low confidence in {skill}. Consider building a project demonstrating this skill.")
        elif confidence < 70:
            if not has_repo_evidence:
                notes.append(f"Add a GitHub project showcasing {skill} to strengthen evidence.")
            if skill not in assessment_scores:
                notes.append(f"Take an assessment in {skill} to validate proficiency.")
        
        if resume_claim and resume_claim.level == SkillLevel.ADVANCED and confidence < 60:
            notes.append(f"Resume claims 'advanced' but evidence suggests lower. Consider adjusting claim or adding proof.")
        
        return " | ".join(notes) if notes else None
    
    def synthesize_no_github(
        self,
        resume_claims: List[SkillClaim],
        assessment_scores: Dict[str, float]
    ) -> ProofCard:
        """Synthesize Proof Card without GitHub evidence (alternative path)."""
        
        all_skills = set()
        for claim in resume_claims:
            all_skills.add(claim.name)
        for skill in assessment_scores:
            all_skills.add(skill)
        
        # Adjusted weights for no-GitHub path
        weights = {
            EvidenceSource.ASSESSMENT: 0.50,
            EvidenceSource.RESUME: 0.20,
            EvidenceSource.VIVA: 0.30,  # Viva carries more weight
        }
        
        unified_skills = []
        
        for skill in sorted(all_skills):
            evidence_bundle = []
            
            # Resume claim
            resume_claim = next((c for c in resume_claims if c.name == skill), None)
            if resume_claim:
                level_weight = {"beginner": 0.3, "intermediate": 0.6, "advanced": 0.9}.get(resume_claim.level.value, 0.3)
                evidence_bundle.append(EvidenceItem(
                    type=EvidenceSource.RESUME,
                    source="resume",
                    detail=f"Claimed as {resume_claim.level.value} in resume",
                    weight=weights[EvidenceSource.RESUME] * level_weight,
                    confidence=level_weight * 0.5
                ))
            
            # Assessment
            if skill in assessment_scores:
                score = assessment_scores[skill]
                norm_score = score / 100.0
                evidence_bundle.append(EvidenceItem(
                    type=EvidenceSource.ASSESSMENT,
                    source="assessment",
                    detail=f"Assessment score: {score:.0f}/100",
                    weight=weights[EvidenceSource.ASSESSMENT] * norm_score,
                    confidence=norm_score
                ))
            
            # Calculate confidence
            total_weight = sum(e.weight for e in evidence_bundle)
            if total_weight > 0:
                weighted_confidence = sum(e.confidence * e.weight for e in evidence_bundle) / total_weight
            else:
                weighted_confidence = 0.0
            
            final_confidence = min(weighted_confidence * 100, 100)
            
            gap_notes = None
            if final_confidence < 50:
                gap_notes = f"No GitHub evidence for {skill}. Viva performance will be critical. Consider creating a portfolio project."
            
            unified_skills.append(UnifiedSkill(
                skill=skill,
                final_confidence=final_confidence,
                evidence_bundle=evidence_bundle,
                tutorial_clone_flag=False,
                gap_notes=gap_notes
            ))
        
        overall_confidence = sum(s.final_confidence for s in unified_skills) / len(unified_skills) if unified_skills else 0
        evidence_coverage = 0.0  # No repo evidence
        
        return ProofCard(
            candidate_id="",
            unified_skills=unified_skills,
            tutorial_clone_flags=[],
            assessment_scores=assessment_scores,
            overall_confidence=overall_confidence,
            evidence_coverage=evidence_coverage
        )