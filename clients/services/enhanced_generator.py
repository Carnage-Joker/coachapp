"""
Enhanced workout generation with improved selection algorithms.
"""
from __future__ import annotations

from typing import Dict, List, Any
from clients.services.generator import _load_exercise_db, _skill_allows


def generate_balanced_week_plan(profile: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Generate a more balanced weekly plan with better movement pattern distribution.
    
    Args:
        profile: Client profile with equipment, goals, constraints
        
    Returns:
        Dictionary mapping day names to exercise lists
    """
    rows = _load_exercise_db()
    if not rows:
        return {}
    
    # Extract profile data
    days_per_week = int(profile.get("days_per_week", 3))
    session_len = int(profile.get("session_length_min", 60))
    skill = str(profile.get("skill_level", "Beginner"))
    allowed_equipment = set(profile.get("equipment_allowed", []))
    disliked = set(profile.get("disliked_exercises", []))
    require_knee = profile.get("require_knee_friendly", False)
    require_shoulder = profile.get("require_shoulder_friendly", False)
    require_back = profile.get("require_back_friendly", False)
    
    # Filter exercises
    filtered: List[Dict[str, str]] = []
    for r in rows:
        # Check dislikes
        if r.get("Exercise") in disliked:
            continue
            
        # Check equipment
        eq = r.get("Equipment", "")
        if eq and eq not in allowed_equipment:
            continue
            
        # Check skill level
        row_level = r.get("Skill Level", "")
        if row_level and not _skill_allows(row_level, skill):
            continue
            
        # Check injury constraints
        if require_knee and r.get("Knee-Friendly", "").upper() != "TRUE":
            continue
        if require_shoulder and r.get("Shoulder-Friendly", "").upper() != "TRUE":
            continue
        if require_back and r.get("Back-Friendly", "").upper() != "TRUE":
            continue
            
        filtered.append(r)
    
    # Categorize by movement pattern
    patterns = {
        "Squat": [],
        "Hinge": [],
        "Horizontal Push": [],
        "Horizontal Pull": [],
        "Vertical Push": [],
        "Vertical Pull": [],
        "Lunge": [],
        "Core – Brace/Anti-Extension": [],
        "Carry/Gait": [],
        "Jump/Power": [],
        "Conditioning": [],
    }
    
    for r in filtered:
        pattern = r.get("Movement Pattern", "")
        if pattern in patterns:
            patterns[pattern].append(r)
    
    # Define training splits based on days per week
    if days_per_week == 3:
        splits = [
            ["Squat", "Horizontal Push", "Horizontal Pull", "Core – Brace/Anti-Extension"],
            ["Hinge", "Vertical Push", "Vertical Pull", "Core – Brace/Anti-Extension"],
            ["Lunge", "Horizontal Push", "Horizontal Pull", "Carry/Gait"],
        ]
    elif days_per_week == 4:
        splits = [
            ["Squat", "Horizontal Push", "Horizontal Pull", "Core – Brace/Anti-Extension"],
            ["Hinge", "Vertical Push", "Vertical Pull"],
            ["Lunge", "Horizontal Push", "Horizontal Pull", "Carry/Gait"],
            ["Squat", "Vertical Push", "Vertical Pull", "Core – Brace/Anti-Extension"],
        ]
    elif days_per_week == 5:
        splits = [
            ["Squat", "Horizontal Push", "Horizontal Pull"],
            ["Hinge", "Vertical Pull", "Core – Brace/Anti-Extension"],
            ["Lunge", "Horizontal Push", "Carry/Gait"],
            ["Squat", "Vertical Push", "Horizontal Pull"],
            ["Hinge", "Vertical Pull", "Core – Brace/Anti-Extension", "Conditioning"],
        ]
    else:  # 2, 6, or 7 days
        splits = [
            ["Squat", "Horizontal Push", "Horizontal Pull", "Core – Brace/Anti-Extension"],
            ["Hinge", "Vertical Push", "Vertical Pull", "Core – Brace/Anti-Extension"],
        ] * ((days_per_week + 1) // 2)
        splits = splits[:days_per_week]
    
    # Generate days
    days = {}
    used_exercises = set()
    
    for day_idx, day_patterns in enumerate(splits, 1):
        day_name = f"Day {day_idx}"
        exercises: List[Dict[str, Any]] = []
        time_remaining = session_len
        
        # Add warm-up
        warmup_pool = [r for r in filtered if r.get("Warm-Up Category")]
        if warmup_pool and time_remaining > 10:
            warmup = warmup_pool[0]
            exercises.append({
                "name": warmup.get("Exercise", "Warm-up"),
                "movement_pattern": None,
                "equipment": None,
                "sets": 1,
                "reps": "5-10 minutes",
                "rest_s": 0,
                "notes": f"Warm-up: {warmup.get('Warm-Up Category', 'General')}",
            })
            time_remaining -= 10
        
        # Add main exercises
        for pattern in day_patterns:
            pool = patterns.get(pattern, [])
            if not pool:
                continue
                
            # Find unused exercise from this pattern
            available = [r for r in pool if r.get("Exercise") not in used_exercises] or pool  # Reuse if necessary

                
            if not available:
                continue
                
            exercise = available[0]
            used_exercises.add(exercise.get("Exercise"))
            
            # Parse exercise details
            sets = int(exercise.get("Default Sets", "3") or 3)
            reps = exercise.get("Default Reps", "10") or "10"
            rest = int((exercise.get("Default Rest (s)", "60") or "60").strip() or 60)
            time_per_set = int(exercise.get("Est. Time/Set", "60") or 60)
            
            # Check time budget
            est_time = sets * (time_per_set + rest)
            if time_remaining - est_time < -10 and len(exercises) > 1:
                continue
                
            time_remaining -= est_time
            
            exercises.append({
                "name": exercise.get("Exercise", "Exercise"),
                "movement_pattern": pattern,
                "equipment": exercise.get("Equipment"),
                "sets": sets,
                "reps": reps,
                "rest_s": rest,
                "notes": exercise.get("Coaching Cues"),
            })
        
        days[day_name] = exercises
    
    return days


def calculate_workout_volume(plan: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
    """
    Calculate total workout volume metrics.
    
    Args:
        plan: Workout plan dictionary
        
    Returns:
        Dictionary with volume metrics
    """
    total_exercises = 0
    total_sets = 0
    patterns_used = set()
    equipment_used = set()
    
    for day_exercises in plan.values():
        total_exercises += len(day_exercises)
        for ex in day_exercises:
            total_sets += ex.get("sets", 0)
            if ex.get("movement_pattern"):
                patterns_used.add(ex["movement_pattern"])
            if ex.get("equipment"):
                equipment_used.add(ex["equipment"])
    
    return {
        "total_exercises": total_exercises,
        "total_sets": total_sets,
        "avg_exercises_per_day": total_exercises / len(plan) if plan else 0,
        "patterns_count": len(patterns_used),
        "equipment_count": len(equipment_used),
        "patterns": sorted(patterns_used),
        "equipment": sorted(equipment_used),
    }
