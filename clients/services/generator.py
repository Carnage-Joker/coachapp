from __future__ import annotations

import csv
from pathlib import Path
from typing import Dict, List, Any, Tuple

from django.conf import settings

from workouts.services.generation import generate_session, SessionParams


def _load_exercise_db() -> List[Dict[str, str]]:
    """
    Load canonical CSV if present. Returns list of row dicts with canonical headers.
    If not found, returns an empty list and we will fall back to an internal library.
    """
    data_dir = Path(getattr(settings, "BASE_DIR", ".")) / "coachapp" / "data"
    csv_path = data_dir / "exercise_db.csv"
    if not csv_path.exists():
        return []
    rows: List[Dict[str, str]] = []
    with csv_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append({k.strip(): (v or "").strip() for k, v in r.items()})
    return rows


def _estimate_time_per_set(row: Dict[str, str]) -> int:
    try:
        return int(row.get("Est. Time/Set", "0") or 0)
    except Exception:
        return 0


def _skill_allows(row_level: str, skill: str) -> bool:
    levels = ["Beginner", "Intermediate", "Advanced"]
    try:
        i_row = levels.index((row_level or "").strip() or "Beginner")
    except ValueError:
        i_row = 0
    try:
        i_skill = levels.index((skill or "Beginner").strip())
    except ValueError:
        i_skill = 0
    return i_row <= i_skill


def _select_warmups(rows: List[Dict[str, str]], count: int = 2) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for r in rows:
        if len(out) >= count:
            break
        if (r.get("Warm-Up Category") or "").strip():
            out.append({
                "name": r.get("Exercise") or "Warm-up",
                "notes": f"Warm-up: {r.get('Warm-Up Category') or ''}",
                "sets": 1,
                "reps": int(r.get("Default Reps", "8") or 8),
                "rest_s": 30,
            })
    return out


def _pick_exercises_from_csv(rows: List[Dict[str, str]], profile: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Very lightweight selection by movement pattern buckets, honoring equipment/location/space/impact and dislikes.
    Output: {"Day 1": [items], ...}
    """
    if not rows:
        return {}

    days = {}
    patterns = [
        "Squat",
        "Hinge",
        "Horizontal Push",
        "Horizontal Pull",
        "Vertical Push",
        "Vertical Pull",
        "Core – Brace/Anti-Extension",
        "Lunge",
        "Carry/Gait",
        "Conditioning",
    ]

    allowed_equipment = set(profile.get("equipment_allowed", []))
    disliked = set(profile.get("disliked_exercises", []))
    days_per_week = int(profile.get("days_per_week", 3))
    session_len = int(profile.get("session_length_min", 60))
    skill = str(profile.get("skill_level", "Beginner"))

    # Filter rows by simple criteria
    filtered: List[Dict[str, str]] = []
    for r in rows:
        if r.get("Exercise") in disliked:
            continue
        eq = r.get("Equipment") or ""
        if eq and eq not in allowed_equipment:
            continue
        row_level = r.get("Skill Level") or ""
        if row_level and not _skill_allows(row_level, skill):
            continue
        # Optional: space/impact gating
        filtered.append(r)

    # Bucket by movement pattern
    by_pat: Dict[str, List[Dict[str, str]]] = {p: [] for p in patterns}
    for r in filtered:
        by_pat.get(r.get("Movement Pattern") or "", []).append(r)

    def take_first(bucket: List[Dict[str, str]], n: int) -> List[Dict[str, str]]:
        return bucket[:n]

    any_pull = False
    for d in range(1, days_per_week + 1):
        items: List[Dict[str, Any]] = []
        budget = session_len
        # Auto warm-ups
        wu = _select_warmups(filtered, count=2)
        for w in wu:
            items.append(w)
            budget -= 5
        # Aim for 4–6 exercises per day
        for pat in ["Squat", "Hinge", "Horizontal Push", "Horizontal Pull", "Core – Brace/Anti-Extension"]:
            pool = by_pat.get(pat, [])
            if not pool:
                continue
            for r in take_first(pool, 1):
                sets = int(r.get("Default Sets", "3") or 3)
                reps = int(r.get("Default Reps", "10") or 10)
                rest = int((r.get("Default Rest (s)") or "60").strip() or 60)
                per_set = _estimate_time_per_set(r) or 60
                est = sets * (per_set + rest)
                if budget - est < -10:
                    continue
                budget -= est
                mp = r.get("Movement Pattern") or None
                if mp and ("Pull" in mp):
                    any_pull = True
                items.append({
                    "name": r.get("Exercise") or "Exercise",
                    "movement_pattern": mp,
                    "equipment": r.get("Equipment") or None,
                    "sets": sets,
                    "reps": reps,
                    "rest_s": rest,
                })
        days[f"Day {d}"] = items

    # Pull coverage guarantee across week
    if not any_pull:
        # try to inject one Horizontal Pull if available
        hp = by_pat.get("Horizontal Pull", []) or by_pat.get("Vertical Pull", [])
        if hp:
            r = hp[0]
            inject = {
                "name": r.get("Exercise") or "Row/Pull",
                "movement_pattern": r.get("Movement Pattern") or "Pull",
                "equipment": r.get("Equipment") or None,
                "sets": int(r.get("Default Sets", "3") or 3),
                "reps": int(r.get("Default Reps", "10") or 10),
                "rest_s": int((r.get("Default Rest (s)") or "60").strip() or 60),
            }
            # place into Day 1
            days.setdefault("Day 1", []).append(inject)

    return days


def _apply_progressive_overload(days: Dict[str, List[Dict[str, Any]]], prior_blocks: int = 0) -> None:
    if prior_blocks <= 0:
        return
    bump_sets = min(2, prior_blocks)  # up to +2 sets at most
    for _, items in days.items():
        count = 0
        for it in items:
            if count >= 2:
                break
            if isinstance(it.get("sets"), int):
                it["sets"] = max(2, min(6, int(it["sets"]) + bump_sets))
                count += 1


def generate_week_plan(client, profile: Dict[str, Any], save: bool = False) -> Dict[str, Any]:
    """
    Try to build a week plan from CSV if available; otherwise fall back to a heuristic session generator.
    Returns a dict with keys: client, plan (mapping of day -> items[])
    """
    rows = _load_exercise_db()
    if rows:
        days = _pick_exercises_from_csv(rows, profile)
    else:
        # Fallback: use internal generator to produce a session per day
        days_per_week = int(profile.get("days_per_week", 3))
        equip = list(profile.get("equipment_allowed", []))
        level = profile.get("skill_level", "Beginner")
        duration = int(profile.get("session_length_min", 50))
        days = {}
        for d in range(1, days_per_week + 1):
            sess = generate_session(SessionParams(
                goal="General Fitness",
                duration_min=duration,
                fitness_level=level,  
                equipment=equip,
                target_muscles=["Full Body", "Core"],
            ))
            # Flatten to simple items list
            items: List[Dict[str, Any]] = []
            for block in sess.get("blocks", []):
                for it in block.get("items", []):
                    items.append({
                        "name": it.get("exercise") or it.get("name") or "Exercise",
                        "sets": it.get("sets"),
                        "reps": it.get("reps"),
                        "rest_s": it.get("rest_s"),
                        "notes": it.get("protocol") or None,
                    })
            days[f"Day {d}"] = items

    # Progressive overload based on prior blocks count
    try:
        prior = getattr(client, "blocks", None)
        prior_count = prior.count() if prior is not None else 0
        _apply_progressive_overload(days, prior_count)
    except Exception:
        pass

    display_name = client.preferred_name or f"{client.first_name} {client.last_name}".strip()
    return {"client": display_name, "plan": days}
