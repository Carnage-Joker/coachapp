from __future__ import annotations

from typing import Dict, List

from ..models import Client


def _equipment_allowed(client: Client) -> List[str]:
    cats = {e.category for e in client.equipment.all()}
    # If none provided, assume Bodyweight minimal
    if not cats:
        cats = {"Bodyweight"}
    return sorted(cats)


def _movement_weights(client: Client) -> Dict[str, float]:
    base = {
        "Squat": 1.0,
        "Hinge": 1.0,
        "Horizontal Push": 1.0,
        "Horizontal Pull": 1.0,
        "Vertical Push": 1.0,
        "Vertical Pull": 1.0,
        "Lunge": 1.0,
        "Core – Brace/Anti-Extension": 1.0,
        "Carry/Gait": 1.0,
        "Jump/Power": 0.8 if client.power_interest else 0.6,
        "Conditioning": 1.0,
    }
    # Preferences can adjust weights
    for pref in client.preferences.all():
        if pref.kind == "Movement Pattern":
            delta = 0.2 if pref.sentiment == "Like" else (-0.4 if pref.sentiment in ("Dislike", "Hard No") else 0.0)
            base[pref.value] = max(0.2, min(2.0, base.get(pref.value, 1.0) + delta))
    return base


def normalize_client_profile(client: Client) -> Dict:
    return {
        "equipment_allowed": _equipment_allowed(client),
        "location": client.primary_location,
        "space_max": client.space_available,
        "impact_max": client.impact_tolerance,
        "require_knee_friendly": bool(client.knee_issue),
        "require_shoulder_friendly": bool(client.shoulder_issue),
        "require_back_friendly": bool(client.back_issue),
        "movement_weights": _movement_weights(client),
        "days_per_week": int(client.days_per_week or 3),
        "session_length_min": int(client.session_length_min or 60),
        "target_rpe": "7-9",
        "skill_level": _skill_level(client),
        "disliked_exercises": [p.value for p in client.preferences.all() if p.kind == "Exercise" and p.sentiment in ("Dislike", "Hard No")],
        "liked_exercises": [p.value for p in client.preferences.all() if p.kind == "Exercise" and p.sentiment == "Like"],
    }


def _skill_level(client: Client) -> str:
    # Simple heuristic: training age → skill level
    try:
        yrs = float(client.training_age_years or 0)
    except Exception:
        yrs = 0.0
    if yrs >= 5:
        return "Advanced"
    if yrs >= 1.5:
        return "Intermediate"
    return "Beginner"

