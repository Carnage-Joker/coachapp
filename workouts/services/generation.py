from __future__ import annotations

from dataclasses import dataclass
from typing import List, Literal, Dict, Any


Goal = Literal[
    "Weight Loss",
    "Muscle Building",
    "Strength Training",
    "Endurance",
    "Flexibility",
    "General Fitness",
]

Level = Literal["Beginner", "Intermediate", "Advanced"]


@dataclass
class SessionParams:
    goal: Goal
    duration_min: int  # desired duration in minutes
    fitness_level: Level
    equipment: List[str]
    target_muscles: List[str]
    intensity: str | None = None
    primary_count: int | None = None
    accessory_count: int | None = None


def _tempo_seconds_per_rep(goal: Goal) -> float:
    # Simple heuristic for time-under-tension per rep
    if goal == "Strength Training":
        return 3.0  # controlled, heavier
    if goal == "Endurance":
        return 1.5  # faster, lower load
    return 2.0  # general / hypertrophy


def _volume_profile(goal: Goal, level: Level):
    # Sets/reps/rest by goal, scaled by level
    mult = {"Beginner": 0.75, "Intermediate": 1.0, "Advanced": 1.2}[level]
    if goal == "Strength Training":
        return {
            "main_sets": max(3, round(4 * mult)),
            "main_reps": 4,
            "main_rest": 150,  # seconds
            "acc_sets": max(2, round(3 * mult)),
            "acc_reps": 8,
            "acc_rest": 90,
        }
    if goal in ("Muscle Building",):
        return {
            "main_sets": max(3, round(4 * mult)),
            "main_reps": 10,
            "main_rest": 75,
            "acc_sets": max(2, round(3 * mult)),
            "acc_reps": 12,
            "acc_rest": 60,
        }
    if goal in ("Weight Loss", "Endurance"):
        return {
            "main_sets": max(3, round(3 * mult)),
            "main_reps": 15,
            "main_rest": 45,
            "acc_sets": max(2, round(2 * mult)),
            "acc_reps": 15,
            "acc_rest": 30,
        }
    # General Fitness / Flexibility fallback
    return {
        "main_sets": max(2, round(3 * mult)),
        "main_reps": 10,
        "main_rest": 60,
        "acc_sets": max(2, round(2 * mult)),
        "acc_reps": 12,
        "acc_rest": 45,
    }


def _default_exercises(equipment: List[str]) -> Dict[str, List[str]]:
    # Minimal library by movement pattern; filtered by equipment where possible
    bodyweight = "Bodyweight" in equipment
    dumbbells = "Dumbbells" in equipment
    barbells = "Barbells" in equipment
    bands = "Resistance Bands" in equipment
    kb = "Kettlebells" in equipment

    choices = {
        "Squat": [
            *(["Back Squat"] if barbells else []),
            *(["Front Squat"] if barbells else []),
            *(["Goblet Squat"] if dumbbells or kb else []),
            *(["Air Squat"] if bodyweight else []),
        ],
        "Hinge": [
            *(["Deadlift"] if barbells else []),
            *(["Romanian Deadlift"] if barbells or dumbbells else []),
            *(["Kettlebell Swing"] if kb else []),
            *(["Hip Hinge Good Morning (band)"] if bands else []),
        ],
        "Push": [
            *(["Bench Press"] if barbells else []),
            *(["DB Bench Press"] if dumbbells else []),
            *(["Push-up"] if bodyweight else []),
            *(["Overhead Press"] if barbells or dumbbells else []),
        ],
        "Pull": [
            *(["Barbell Row"] if barbells else []),
            *(["DB Row"] if dumbbells else []),
            *(["Band Row"] if bands else []),
            *(["Pull-up / Assisted"] if bodyweight else []),
        ],
        "Lunge": [
            *(["Walking Lunge"] if bodyweight or dumbbells or kb else []),
            *(["Split Squat"] if bodyweight or dumbbells or kb else []),
        ],
        "Core": [
            "Plank",
            "Side Plank",
            "Dead Bug",
            *(["Hollow Hold"] if bodyweight else []),
        ],
        "Carry": [
            *(["Farmer Carry"] if dumbbells or kb else []),
        ],
        "Conditioning": [
            "Burpees",
            "Mountain Climbers",
            *(["KB Snatch"] if kb else []),
            *(["Jump Rope"] if bodyweight else []),
        ],
        "Mobility": [
            "T-Spine Opener",
            "Hip Flexor Stretch",
            "Ankle Dorsiflexion Drill",
            "Shoulder CARs",
        ],
    }
    # Remove empty categories
    return {k: [x for x in v if x] for k, v in choices.items() if any(v)}


def _pick(lst: List[str]) -> str:
    return lst[0] if lst else ""


def estimate_minutes(sets: int, reps: int, rest_s: int, tempo_s_per_rep: float) -> float:
    # Rough estimate: total work time + rest between sets (n-1)
    work = sets * reps * tempo_s_per_rep
    rest = max(0, sets - 1) * rest_s
    return (work + rest) / 60.0


def generate_session(params: SessionParams) -> Dict[str, Any]:
    """
    Generates a single-session workout tailored to goal, equipment, and level, aiming for target duration.
    Applies general programming rules (balanced patterns, warm-up, rep/rest ranges).
    """
    lib = _default_exercises(params.equipment)
    prof = _volume_profile(params.goal, params.fitness_level)
    tempo = _tempo_seconds_per_rep(params.goal)

    # Warm-up block (mobility + ramp-up)
    warmup = {
        "name": "Warm-up",
        "items": [
            {"exercise": _pick(lib.get("Mobility", [])), "duration_min": 4},
            {"exercise": "Ramp-up Sets", "details": "2 light sets for first main lift", "duration_min": 4},
        ],
        "duration_min": 8,
    }

    # Main block: choose 2-3 primary patterns (squat/hinge/push/pull)
    primaries = []
    max_prim = params.primary_count or 3
    for pattern in ("Squat", "Hinge", "Push", "Pull"):
        if lib.get(pattern):
            primaries.append({
                "exercise": _pick(lib[pattern]),
                "sets": prof["main_sets"],
                "reps": prof["main_reps"],
                "rest_s": prof["main_rest"],
                "pattern": pattern,
            })
        if len(primaries) >= max_prim:
            break

    # Accessory block: unilateral/core/carry based on library
    accessories = []
    max_acc = params.accessory_count if isinstance(params.accessory_count, int) and params.accessory_count >= 0 else None
    if lib.get("Lunge"):
        if max_acc is None or len(accessories) < max_acc:
            accessories.append({
                "exercise": _pick(lib["Lunge"]),
                "sets": prof["acc_sets"],
                "reps": prof["acc_reps"],
                "rest_s": prof["acc_rest"],
                "pattern": "Unilateral",
            })
    if lib.get("Core"):
        if max_acc is None or len(accessories) < max_acc:
            accessories.append({
                "exercise": _pick(lib["Core"]),
                "sets": prof["acc_sets"],
                "reps": 30 if params.goal in ("Endurance", "Weight Loss") else 12,
                "rest_s": 45,
                "pattern": "Core",
            })
    if lib.get("Carry"):
        if max_acc is None or len(accessories) < max_acc:
            accessories.append({
                "exercise": _pick(lib["Carry"]),
                "sets": 3,
                "reps": 30,  # meters/seconds
                "rest_s": 60,
                "pattern": "Carry",
            })

    # Finisher for conditioning-oriented goals
    finisher = None
    if params.goal in ("Weight Loss", "Endurance", "General Fitness") and lib.get("Conditioning"):
        finisher = {
            "name": "Finisher",
            "items": [
                {
                    "exercise": _pick(lib["Conditioning"]),
                    "protocol": "EMOM 8 min: 30s work / 30s rest",
                    "duration_min": 8,
                }
            ],
            "duration_min": 8,
        }

    # Build blocks and estimate total duration; adjust accessories to fit target duration
    main_minutes = sum(
        estimate_minutes(it["sets"], int(it["reps"]), it["rest_s"], tempo) for it in primaries
    )
    acc_minutes = sum(
        estimate_minutes(it["sets"], int(it["reps"]) if isinstance(it["reps"], int) else 12, it["rest_s"], 1.8)
        for it in accessories
    )
    total = warmup["duration_min"] + main_minutes + acc_minutes + (finisher["duration_min"] if finisher else 0)

    # Adjust accessory volume to fit target duration window (±10%)
    target = max(20, min(120, params.duration_min))
    lower, upper = target * 0.9, target * 1.1
    # Reduce accessory sets if over upper bound
    if total > upper:
        for it in accessories:
            if it["sets"] > 2:
                it["sets"] -= 1
        acc_minutes = sum(
            estimate_minutes(it["sets"], int(it["reps"]) if isinstance(it["reps"], int) else 12, it["rest_s"], 1.8)
            for it in accessories
        )
        total = warmup["duration_min"] + main_minutes + acc_minutes + (finisher["duration_min"] if finisher else 0)
    # If still over, drop finisher
    if finisher and total > upper:
        finisher = None
        total = warmup["duration_min"] + main_minutes + acc_minutes
    # If under lower, add a core set
    if total < lower and lib.get("Core"):
        accessories.append({
            "exercise": _pick(lib["Core"]),
            "sets": 2,
            "reps": 12,
            "rest_s": 45,
            "pattern": "Core",
        })
        acc_minutes = sum(
            estimate_minutes(it["sets"], int(it["reps"]) if isinstance(it["reps"], int) else 12, it["rest_s"], 1.8)
            for it in accessories
        )
        total = warmup["duration_min"] + main_minutes + acc_minutes + (finisher["duration_min"] if finisher else 0)

    blocks = [
        warmup,
        {"name": "Main", "items": primaries, "duration_min": round(main_minutes)},
        {"name": "Accessories", "items": accessories, "duration_min": round(acc_minutes)},
    ]
    if finisher:
        blocks.append(finisher)

    return {
        "goal": params.goal,
        "fitness_level": params.fitness_level,
        "estimated_duration_min": round(total),
        "target_duration_min": target,
        "blocks": blocks,
    }


def generate_plan(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate a multi-week plan using the session generator.
    Expects: weeks (int), days_per_week (int), other SessionParams keys.
    """
    weeks = int(params.get("weeks", 4))
    days_per_week = int(params.get("days_per_week", 3))

    base = SessionParams(
        goal=params["goal"],
        duration_min=int(params.get("duration_min", 50)),
        fitness_level=params.get("fitness_level", "Intermediate"),
        equipment=params.get("equipment", []),
        target_muscles=params.get("target_muscles", []),
        intensity=params.get("intensity"),
        primary_count=(int(params.get("primary_count")) if str(params.get("primary_count", "")).isdigit() else None),
        accessory_count=(int(params.get("accessory_count")) if str(params.get("accessory_count", "")).isdigit() else None),
    )

    plan: Dict[str, Any] = {"weeks": []}
    for w in range(1, weeks + 1):
        week = {"week": w, "days": []}
        for d in range(1, days_per_week + 1):
            # Rotate emphases across the week: lower / upper / full
            if d % 3 == 1:
                tm = ["Legs", "Glutes", "Core"]
            elif d % 3 == 2:
                tm = ["Chest", "Back", "Shoulders", "Arms", "Core"]
            else:
                tm = ["Full Body", "Core"]
            sess = generate_session(SessionParams(
                goal=base.goal,
                duration_min=base.duration_min,
                fitness_level=base.fitness_level, 
                equipment=base.equipment,
                target_muscles=tm,
                intensity=base.intensity,
                primary_count=base.primary_count,
                accessory_count=base.accessory_count,
            ))
            week["days"].append({"day": f"Week {w} Day {d}", "session": sess})
        plan["weeks"].append(week)

    return plan

