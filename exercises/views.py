from __future__ import annotations

import csv
from pathlib import Path
from typing import Any, Dict, List

from django.conf import settings
from rest_framework import views, permissions
from rest_framework.response import Response


CANONICAL_COLUMNS = [
    "Exercise ID",
    "Exercise",
    "Compound",
    "Movement Pattern",
    "Default Reps",
    "Default Sets",
    "Default Rest (s)",
    "Unilateral/Bilateral",
    "Equipment",
    "Location Suitability",
    "Space Needed",
    "Impact Level",
    "Knee-Friendly",
    "Shoulder-Friendly",
    "Back-Friendly",
    "Skill Level",
    "Target RPE",
    "Tempo",
    "Metcon Score (1-5)",
    "Contraindications",
    "Coaching Cues",
    "Video URL",
    "Tags",
    "Body Region",
    "Primary Muscle Group",
    "Plane of Motion",
    "Force Vector",
    "Load Type",
    "Home-Friendly",
    "Outdoor-Friendly",
    "Warm-Up Category",
    "Est. Time/Set",
]


def _csv_rows() -> List[Dict[str, str]]:
    base = Path(getattr(settings, "BASE_DIR", ".")) / "coachapp" / "data"
    path = base / "exercise_db.csv"
    if not path.exists():
        return []
    rows: List[Dict[str, str]] = []
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append({k.strip(): (v or "").strip() for k, v in r.items()})
    return rows


def _fallback_rows() -> List[Dict[str, Any]]:
    # Small internal library for dev if CSV not present
    return [
        {
            "Exercise ID": "BW-001",
            "Exercise": "Push-up",
            "Compound": "TRUE",
            "Movement Pattern": "Horizontal Push",
            "Default Reps": "10",
            "Default Sets": "3",
            "Default Rest (s)": "60",
            "Unilateral/Bilateral": "Bilateral",
            "Equipment": "Bodyweight",
            "Location Suitability": "Home,Gym",
            "Space Needed": "Small",
            "Impact Level": "Low",
            "Knee-Friendly": "TRUE",
            "Shoulder-Friendly": "TRUE",
            "Back-Friendly": "TRUE",
            "Skill Level": "Beginner",
            "Target RPE": "7-9",
            "Tempo": "2011",
            "Metcon Score (1-5)": "3",
            "Contraindications": "",
            "Coaching Cues": "Brace core, full ROM",
            "Video URL": "",
            "Tags": "Upper,Chest,Triceps",
            "Body Region": "Upper",
            "Primary Muscle Group": "Chest",
            "Plane of Motion": "Transverse",
            "Force Vector": "Horizontal",
            "Load Type": "Bodyweight",
            "Home-Friendly": "TRUE",
            "Outdoor-Friendly": "TRUE",
            "Warm-Up Category": "",
            "Est. Time/Set": "60",
        },
        {
            "Exercise ID": "KB-101",
            "Exercise": "Kettlebell Swing",
            "Compound": "TRUE",
            "Movement Pattern": "Hinge",
            "Default Reps": "12",
            "Default Sets": "4",
            "Default Rest (s)": "75",
            "Unilateral/Bilateral": "Bilateral",
            "Equipment": "Kettlebell",
            "Location Suitability": "Home,Gym,Outdoor",
            "Space Needed": "Medium",
            "Impact Level": "Moderate",
            "Knee-Friendly": "TRUE",
            "Shoulder-Friendly": "TRUE",
            "Back-Friendly": "TRUE",
            "Skill Level": "Intermediate",
            "Target RPE": "7-9",
            "Tempo": "X1X1",
            "Metcon Score (1-5)": "4",
            "Contraindications": "",
            "Coaching Cues": "Hinge, snap hips",
            "Video URL": "",
            "Tags": "Full Body",
            "Body Region": "Full Body",
            "Primary Muscle Group": "Glutes",
            "Plane of Motion": "Sagittal",
            "Force Vector": "Horizontal",
            "Load Type": "Free Weight",
            "Home-Friendly": "TRUE",
            "Outdoor-Friendly": "TRUE",
            "Warm-Up Category": "",
            "Est. Time/Set": "60",
        },
    ]


class ExerciseListView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        rows = _csv_rows() or _fallback_rows()
        return Response({
            "columns": CANONICAL_COLUMNS,
            "count": len(rows),
            "items": rows,
        })


class ExerciseSchemaView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        return Response({"columns": CANONICAL_COLUMNS})
