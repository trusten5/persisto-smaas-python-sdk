# backend/utils/retrieval_profiles.py
from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, TypedDict


# ------------------------
# Retrieval profile config
# ------------------------

@dataclass(frozen=True)
class RetrievalProfile:
    name: str
    # number to return to caller (default, can be overridden per-call)
    k: int = 5
    # how many to fetch from vector search before reranking
    oversample: int = 20
    # minimum raw cosine similarity to keep a hit (0..1)
    min_sim: float = 0.4
    # linear recency boost: score = eff_sim + recency_weight * recency_norm
    recency_weight: float = 0.0
    # how “recent” is normalized; newer = closer to 1.0 within this window
    recency_window_secs: int = 7 * 24 * 3600
    # optional exponential time decay half-life (days). If set, eff_sim = sim * decay
    time_decay_half_life_days: Optional[float] = None


# Default profiles used by get_profile(mode)
DEFAULT_PROFILES: Dict[str, RetrievalProfile] = {
    "strict": RetrievalProfile(
        name="strict",
        k=12,
        oversample=60,
        min_sim=0.45,
        recency_weight=0.0,
    ),
    "fuzzy": RetrievalProfile(
        name="fuzzy",
        k=24,
        oversample=80,
        min_sim=0.20,
        recency_weight=0.0,
    ),
    "recency": RetrievalProfile(
        name="recency",
        k=16,
        oversample=80,
        min_sim=0.30,
        recency_weight=0.18,
        time_decay_half_life_days=7.0,
    ),
}


def get_profile(name: Optional[str]) -> RetrievalProfile:
    """
    Return a *copy* of the named default profile so callers can override fields
    without mutating the shared defaults.
    """
    key = (name or "strict").lower()
    base = DEFAULT_PROFILES.get(key, DEFAULT_PROFILES["strict"])
    # dataclasses.replace produces a new instance
    return replace(base)


# ------------------------
# Reranker helpers
# ------------------------

def _parse_dt(dt: Any) -> Optional[datetime]:
    if isinstance(dt, datetime):
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    if isinstance(dt, str):
        try:
            d = datetime.fromisoformat(dt.replace("Z", "+00:00"))
            return d if d.tzinfo else d.replace(tzinfo=timezone.utc)
        except Exception:
            return None
    return None


def _recency_norm(created_at: Optional[datetime], now: datetime, window_secs: int) -> float:
    """Normalize recency to [0..1]; brand new ~= 1, older than window -> 0."""
    if not created_at:
        return 0.0
    age = max(0.0, (now - created_at).total_seconds())
    if age >= window_secs:
        return 0.0
    return 1.0 - (age / float(window_secs))


def _time_decay_weight(created_at: Optional[datetime], half_life_days: Optional[float]) -> float:
    """Exponential decay weight in (0..1], 1.0 = no decay / brand new."""
    if not created_at or not half_life_days:
        return 1.0
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)
    age_days = (datetime.now(timezone.utc) - created_at).total_seconds() / 86400.0
    return 0.5 ** (age_days / float(half_life_days))


class RawHit(TypedDict, total=False):
    id: str
    content: str
    metadata: dict
    created_at: Optional[datetime]
    similarity: float  # raw cosine sim from vector DB
    score: float       # final reranked score


def rerank_hits(
    raw_hits: List[Dict[str, Any]],
    profile: RetrievalProfile,
    k_override: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """
    Rerank pipeline:
      1) Drop hits with raw similarity < profile.min_sim
      2) eff_sim = similarity * time_decay_weight(created_at, half_life_days)   (if configured)
      3) recency_norm = recency within window (0..1)
      4) final score = eff_sim + profile.recency_weight * recency_norm
      5) Sort by score desc (tie-breaker: similarity), then truncate to k
    """
    if not raw_hits:
        return []

    now = datetime.now(timezone.utc)
    kept: List[Dict[str, Any]] = []

    for h in raw_hits:
        sim = float(h.get("similarity", 0.0))
        if sim < profile.min_sim:
            continue

        created_dt = _parse_dt(h.get("created_at"))
        decay = _time_decay_weight(created_dt, profile.time_decay_half_life_days)
        eff_sim = sim * decay

        rec = _recency_norm(created_dt, now, profile.recency_window_secs) if profile.recency_weight > 0 else 0.0
        score = eff_sim + (profile.recency_weight * rec)

        kept.append({
            "id": h.get("id"),
            "content": h.get("content"),
            "metadata": h.get("metadata") or {},
            "created_at": h.get("created_at"),
            "similarity": sim,
            "score": score,
        })

    if not kept:
        return []

    kept.sort(key=lambda x: (x["score"], x["similarity"]), reverse=True)
    k = int(k_override or profile.k)
    return kept[:k]
