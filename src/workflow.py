"""Self-checking recommendation workflow integrated with the original scorer.

This deterministic reliability mechanism is deliberately not presented as a
trained language model or a generative-AI/RAG implementation. It validates,
recommends, verifies, and optionally revises rankings in one application path.
"""

from dataclasses import dataclass
import logging
import math
from typing import Dict, List, Tuple

from .recommender import recommend_songs

LOGGER = logging.getLogger(__name__)
ENERGY_TOLERANCE = 0.30

Recommendation = Tuple[Dict, float, str]


@dataclass
class WorkflowResult:
    """Output plus a transparent audit trail for the reliability loop."""

    profile: Dict
    recommendations: List[Recommendation]
    initial_top: str
    revised: bool
    check_status: str
    notes: List[str]


def _clean_profile(user_prefs: Dict) -> Dict:
    if not isinstance(user_prefs, dict):
        raise ValueError("Preferences must be a dictionary.")

    for field in ("favorite_genre", "favorite_mood"):
        value = user_prefs.get(field)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{field} must be a nonempty text value.")

    raw_energy = user_prefs.get("target_energy")
    if isinstance(raw_energy, bool):
        raise ValueError("target_energy must be a number between 0 and 1.")
    try:
        energy = float(raw_energy)
    except (TypeError, ValueError) as exc:
        raise ValueError("target_energy must be a number between 0 and 1.") from exc
    if not math.isfinite(energy) or not 0 <= energy <= 1:
        raise ValueError("target_energy must be a finite number between 0 and 1.")

    return {
        "favorite_genre": user_prefs["favorite_genre"].strip().lower(),
        "favorite_mood": user_prefs["favorite_mood"].strip().lower(),
        "target_energy": energy,
    }


def _check_catalog(songs: List[Dict]) -> None:
    if not songs:
        raise ValueError("Song catalog is empty; recommendations cannot be generated.")
    ids = set()
    for index, song in enumerate(songs, start=1):
        for field in ("id", "title", "artist", "genre", "mood", "energy"):
            if field not in song:
                raise ValueError(f"Song #{index} is missing '{field}'.")
        for field in ("title", "artist", "genre", "mood"):
            if not str(song[field]).strip():
                raise ValueError(f"Song #{index} has an empty '{field}'.")
        try:
            energy = float(song["energy"])
        except (ValueError, TypeError) as exc:
            raise ValueError(f"Song #{index} has invalid energy.") from exc
        if not math.isfinite(energy) or not 0 <= energy <= 1:
            raise ValueError(f"Song #{index} has energy outside 0–1.")
        if song["id"] in ids:
            raise ValueError(f"Duplicate song ID: {song['id']}.")
        ids.add(song["id"])


def _fits_all_preferences(song: Dict, profile: Dict) -> bool:
    return (
        song["genre"].strip().lower() == profile["favorite_genre"]
        and song["mood"].strip().lower() == profile["favorite_mood"]
        and abs(float(song["energy"]) - profile["target_energy"]) <= ENERGY_TOLERANCE
    )


def _mood_and_energy_conflict(song: Dict, profile: Dict) -> bool:
    """Catch a particularly misleading high-ranked recommendation."""
    return (
        song["mood"].strip().lower() != profile["favorite_mood"]
        and abs(float(song["energy"]) - profile["target_energy"]) > ENERGY_TOLERANCE
    )


def _balanced_score(song: Dict, profile: Dict) -> Tuple[float, str]:
    """One guarded retry: mood and energy matter more than exact genre."""
    genre_points = 1.0 if song["genre"].strip().lower() == profile["favorite_genre"] else 0.0
    mood_points = 1.0 if song["mood"].strip().lower() == profile["favorite_mood"] else 0.0
    energy_points = 2.0 * max(0.0, 1.0 - abs(float(song["energy"]) - profile["target_energy"]))
    reasons = (
        f"genre match (+{genre_points:.1f}); "
        f"mood match (+{mood_points:.1f}); "
        f"energy similarity (+{energy_points:.2f}); "
        "balanced retry weights (genre=1, mood=1, energy=2)"
    )
    return round(genre_points + mood_points + energy_points, 2), reasons


def run_workflow(user_prefs: Dict, songs: List[Dict], k: int = 5) -> WorkflowResult:
    """Validate → rank → audit → optionally repair → report limitations.

    Bounded to one repair pass. No hallucinated songs, silent substitutions,
    external services, or unverified claims of recommendation accuracy.
    """
    profile = _clean_profile(user_prefs)
    _check_catalog(songs)
    if isinstance(k, bool) or not isinstance(k, int) or not 1 <= k <= len(songs):
        raise ValueError(f"top-k must be between 1 and {len(songs)}.")

    baseline = recommend_songs(profile, songs, k=k)
    initial_top = baseline[0][0]["title"]
    revised = _mood_and_energy_conflict(baseline[0][0], profile)
    notes: List[str] = []
    recommendations = baseline

    if revised:
        LOGGER.info("Top recommendation failed mood-and-energy check; retrying once with balanced weights")
        rescored = []
        for song in songs:
            score, explanation = _balanced_score(song, profile)
            rescored.append((song, score, explanation))
        recommendations = sorted(rescored, key=lambda item: (-item[1], int(item[0]["id"])))[:k]
        notes.append(
            f"Self-check revised first choice from '{initial_top}' to "
            f"'{recommendations[0][0]['title']}' after detecting a mood-and-energy conflict."
        )

    if not any(_fits_all_preferences(song, profile) for song in songs):
        notes.append(
            "Catalog limitation: no available song matches genre, mood, and "
            f"energy within ±{ENERGY_TOLERANCE:.2f}; results are best-effort matches."
        )

    if _mood_and_energy_conflict(recommendations[0][0], profile):
        notes.append("Top result still conflicts with requested mood and energy; user review advised.")
        status = "REVIEW"
    elif not _fits_all_preferences(recommendations[0][0], profile):
        status = "PARTIAL"
    else:
        status = "PASS"

    return WorkflowResult(profile, recommendations, initial_top, revised, status, notes)
