# src/services/imats_client.py
"""
IMATS Sandbox Client — Push proof cards, rankings; pull shortlist decisions.
"""
import json
import httpx
from typing import List, Dict, Optional
from src.models.schemas import *
from src.config.settings import settings


class IMATSClient:
    def __init__(self, base_url: str = None, api_key: str = None):
        self.base_url = base_url or settings.IMATS_API_URL
        self.api_key = api_key or settings.IMATS_API_KEY
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            timeout=60.0
        )
    
    async def push_proof_cards(self, cards: List[ProofCard]) -> Dict:
        """Push proof cards to IMATS sandbox."""
        payload = {
            "proof_cards": [
                {
                    "candidate_id": card.candidate_id,
                    "unified_skills": [s.model_dump() for s in card.unified_skills],
                    "tutorial_clone_flags": [f.model_dump() for f in card.tutorial_clone_flags],
                    "assessment_scores": card.assessment_scores,
                    "overall_confidence": card.overall_confidence,
                    "evidence_coverage": card.evidence_coverage,
                    "generated_at": card.generated_at.isoformat()
                }
                for card in cards
            ]
        }
        
        try:
            response = await self.client.post("/api/v1/proof-cards/batch", json=payload)
            response.raise_for_status()
            return {"status": "success", "response": response.json()}
        except httpx.HTTPStatusError as e:
            return {"status": "failed", "error": f"HTTP {e.response.status_code}: {e.response.text}"}
        except Exception as e:
            return {"status": "failed", "error": str(e)}
    
    async def push_rankings(self, rankings: List[RankedCandidate], jd_id: str) -> Dict:
        """Push candidate rankings for a JD."""
        payload = {
            "jd_id": jd_id,
            "rankings": [
                {
                    "candidate_id": r.candidate_id,
                    "rank": r.rank,
                    "score": r.score.total_score,
                    "skill_scores": r.score.skill_scores,
                    "reasons": r.reasons,
                    "comparison": {k: v.model_dump() for k, v in r.comparison.items()}
                }
                for r in rankings
            ]
        }
        
        try:
            response = await self.client.post("/api/v1/rankings/batch", json=payload)
            response.raise_for_status()
            return {"status": "success", "response": response.json()}
        except httpx.HTTPStatusError as e:
            return {"status": "failed", "error": f"HTTP {e.response.status_code}: {e.response.text}"}
        except Exception as e:
            return {"status": "failed", "error": str(e)}
    
    async def pull_shortlist_decisions(self, jd_ids: List[str]) -> List[ShortlistDecision]:
        """Pull recruiter shortlist decisions from IMATS."""
        jd_params = ",".join(jd_ids)
        
        try:
            response = await self.client.get(f"/api/v1/shortlist-decisions?jd_ids={jd_params}")
            response.raise_for_status()
            
            data = response.json()
            decisions = []
            
            for item in data.get("decisions", []):
                decisions.append(ShortlistDecision(
                    jd_id=item["jd_id"],
                    candidate_id=item["candidate_id"],
                    decision=item["decision"],
                    notes=item.get("notes"),
                    decided_at=item["decided_at"]
                ))
            
            return decisions
            
        except httpx.HTTPStatusError as e:
            print(f"IMATS pull failed: {e.response.status_code}")
            return []
        except Exception as e:
            print(f"IMATS pull error: {e}")
            return []
    
    async def push_final_scores(self, scores: List[FinalScore]) -> Dict:
        """Push final scores to IMATS."""
        payload = {
            "scores": [
                {
                    "candidate_id": s.candidate_id,
                    "evidence_strength": s.evidence_strength,
                    "viva_performance": s.viva_performance,
                    "assessment_score": s.assessment_score,
                    "consistency": s.consistency,
                    "total_score": s.total_score,
                    "skill_scores": s.skill_scores,
                    "reasons": s.reasons
                }
                for s in scores
            ]
        }
        
        try:
            response = await self.client.post("/api/v1/scores/batch", json=payload)
            response.raise_for_status()
            return {"status": "success", "response": response.json()}
        except Exception as e:
            return {"status": "failed", "error": str(e)}
    
    async def health_check(self) -> bool:
        """Check if IMATS API is reachable."""
        try:
            response = await self.client.get("/health", timeout=10.0)
            return response.status_code == 200
        except:
            return False
    
    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()


# Synchronous wrapper for Streamlit (which doesn't support async well)
class SyncIMATSClient:
    """Synchronous IMATS client for use in Streamlit."""
    
    def __init__(self, base_url: str = None, api_key: str = None):
        self.base_url = base_url or settings.IMATS_API_URL
        self.api_key = api_key or settings.IMATS_API_KEY
        self.client = httpx.Client(
            base_url=self.base_url,
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            timeout=60.0
        )
    
    def push_proof_cards(self, cards: List[ProofCard]) -> Dict:
        """Push proof cards (sync)."""
        payload = {
            "proof_cards": [
                {
                    "candidate_id": card.candidate_id,
                    "unified_skills": [s.model_dump() for s in card.unified_skills],
                    "tutorial_clone_flags": [f.model_dump() for f in card.tutorial_clone_flags],
                    "assessment_scores": card.assessment_scores,
                    "overall_confidence": card.overall_confidence,
                    "evidence_coverage": card.evidence_coverage,
                    "generated_at": card.generated_at.isoformat()
                }
                for card in cards
            ]
        }
        
        try:
            response = self.client.post("/api/v1/proof-cards/batch", json=payload)
            response.raise_for_status()
            return {"status": "success", "response": response.json()}
        except Exception as e:
            return {"status": "failed", "error": str(e)}
    
    def push_rankings(self, rankings: List[RankedCandidate], jd_id: str) -> Dict:
        """Push rankings (sync)."""
        payload = {
            "jd_id": jd_id,
            "rankings": [
                {
                    "candidate_id": r.candidate_id,
                    "rank": r.rank,
                    "score": r.score.total_score,
                    "skill_scores": r.score.skill_scores,
                    "reasons": r.reasons,
                    "comparison": {k: v.model_dump() for k, v in r.comparison.items()}
                }
                for r in rankings
            ]
        }
        
        try:
            response = self.client.post("/api/v1/rankings/batch", json=payload)
            response.raise_for_status()
            return {"status": "success", "response": response.json()}
        except Exception as e:
            return {"status": "failed", "error": str(e)}
    
    def pull_shortlist_decisions(self, jd_ids: List[str]) -> List[ShortlistDecision]:
        """Pull shortlist decisions (sync)."""
        jd_params = ",".join(jd_ids)
        
        try:
            response = self.client.get(f"/api/v1/shortlist-decisions?jd_ids={jd_params}")
            response.raise_for_status()
            
            data = response.json()
            decisions = []
            
            for item in data.get("decisions", []):
                decisions.append(ShortlistDecision(
                    jd_id=item["jd_id"],
                    candidate_id=item["candidate_id"],
                    decision=item["decision"],
                    notes=item.get("notes"),
                    decided_at=item["decided_at"]
                ))
            
            return decisions
            
        except Exception as e:
            print(f"IMATS pull error: {e}")
            return []
    
    def close(self):
        """Close HTTP client."""
        self.client.close()


# Mock client for development/demo
class MockIMATSClient:
    """Mock IMATS client for development when sandbox is unavailable."""
    
    def __init__(self):
        self.stored_cards = []
        self.stored_rankings = []
        self.stored_decisions = [
            ShortlistDecision(jd_id="JD-001", candidate_id="CAND-0042", decision="shortlisted", 
                            notes="Strong backend skills", decided_at="2026-10-30T10:00:00"),
            ShortlistDecision(jd_id="JD-001", candidate_id="CAND-0117", decision="rejected",
                            notes="Insufficient evidence", decided_at="2026-10-30T10:00:00"),
        ]
    
    def push_proof_cards(self, cards: List[ProofCard]) -> Dict:
        self.stored_cards.extend(cards)
        return {"status": "success", "response": {"stored": len(cards)}}
    
    def push_rankings(self, rankings: List[RankedCandidate], jd_id: str) -> Dict:
        self.stored_rankings.extend([{"jd_id": jd_id, **r.model_dump()} for r in rankings])
        return {"status": "success", "response": {"stored": len(rankings)}}
    
    def pull_shortlist_decisions(self, jd_ids: List[str]) -> List[ShortlistDecision]:
        return [d for d in self.stored_decisions if d.jd_id in jd_ids]
    
    async def push_proof_cards_async(self, cards: List[ProofCard]) -> Dict:
        return self.push_proof_cards(cards)
    
    async def push_rankings_async(self, rankings: List[RankedCandidate], jd_id: str) -> Dict:
        return self.push_rankings(rankings, jd_id)
    
    async def pull_shortlist_decisions_async(self, jd_ids: List[str]) -> List[ShortlistDecision]:
        return self.pull_shortlist_decisions(jd_ids)