from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, List, Optional, TypedDict

class RawHit(TypedDict, total=False):
    id: str
    content: str
    metadata: dict
    created_at: Optional[datetime]
    similarity: float   # cosine similarity, 0..1
    score: float        # set during rerank

@dataclass(frozen=True)
class RetrievalProfile:
    name: str
    min_sim: float
    k: int
    oversample: int
    time_decay_half_life_days: Optional[float] = None
    blend_sim_weight: float = 0.7

DEFAULT_PROFILES: Dict[str, RetrievalProfile] = {
    "strict":  RetrievalProfile(name="strict",  min_sim=0.65, k=12, oversample=60),
    "fuzzy":   RetrievalProfile(name="fuzzy",   min_sim=0.35, k=24, oversample=80),
    "recency": RetrievalProfile(name="recency", min_sim=0.40, k=16, oversample=80, time_decay_half_life_days=7.0),
}

def get_profile(name: Optional[str]) -> RetrievalProfile:
    return DEFAULT_PROFILES.get(name or "strict", DEFAULT_PROFILES["strict"])

def time_decay_weight(created_at: Optional[datetime], half_life_days: Optional[float]) -> float:
    if not created_at or not half_life_days:
        return 1.0
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)
    age_days = (datetime.now(timezone.utc) - created_at).total_seconds() / 86400.0
    return 0.5 ** (age_days / half_life_days)

def rerank_hits(
    hits: List[RawHit],
    profile: RetrievalProfile,
    k_override: Optional[int] = None
) -> List[RawHit]:
    out: List[RawHit] = []
    for h in hits:
        sim = float(h.get("similarity", 0.0))
        if sim < profile.min_sim:
            continue
        if profile.time_decay_half_life_days:
            w = time_decay_weight(h.get("created_at"), profile.time_decay_half_life_days)
            score = profile.blend_sim_weight * sim + (1.0 - profile.blend_sim_weight) * w
        else:
            score = sim
        h["score"] = score
        out.append(h)

    out.sort(key=lambda x: x["score"], reverse=True)
    k = k_override or profile.k
    return out[:k]
