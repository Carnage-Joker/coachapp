from __future__ import annotations

import json
from datetime import datetime
from typing import List, Dict, Any, Optional

from django.conf import settings

from workouts.services.generation import generate_session, generate_plan, SessionParams


SYSTEM_PROMPT = (
    "You are an expert personal trainer and nutrition coach. "
    "Help the user by asking concise, high-value questions and producing clear output when enough info is known. "
    "When the user asks for a workout or program, prefer using the provided tools to generate structured plans. "
    "If a meal plan is requested, produce a realistic, balanced 1-7 day plan with calories and macros per meal. "
    "Return short, practical explanations. Keep the tone supportive."
)


def _tool_defs() -> List[Dict[str, Any]]:
    return [
        {
            "type": "function",
            "function": {
                "name": "generate_training_session",
                "description": "Generate a single training session given context.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "goal": {"type": "string"},
                        "duration_min": {"type": "integer"},
                        "fitness_level": {"type": "string", "enum": ["Beginner", "Intermediate", "Advanced"]},
                        "equipment": {"type": "array", "items": {"type": "string"}},
                        "target_muscles": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": ["goal", "duration_min", "fitness_level"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "generate_training_program",
                "description": "Generate a multi-week training program.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "weeks": {"type": "integer"},
                        "days_per_week": {"type": "integer"},
                        "goal": {"type": "string"},
                        "duration_min": {"type": "integer"},
                        "fitness_level": {"type": "string", "enum": ["Beginner", "Intermediate", "Advanced"]},
                        "equipment": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": ["weeks", "days_per_week", "goal", "duration_min", "fitness_level"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "generate_meal_plan",
                "description": "Generate a daily or multi-day meal plan with macros per meal.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "days": {"type": "integer", "minimum": 1, "maximum": 14},
                        "calories": {"type": "integer", "minimum": 1000, "maximum": 5000},
                        "meals_per_day": {"type": "integer", "minimum": 2, "maximum": 6},
                        "diet": {"type": "string", "description": "e.g., balanced, high-protein, vegetarian, vegan, keto"},
                        "protein_g": {"type": "integer"},
                        "fat_g": {"type": "integer"},
                        "carbs_g": {"type": "integer"},
                    },
                },
            },
        },
    ]


def _run_tool(name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    if name == "generate_training_session":
        sp = SessionParams(
            goal=arguments.get("goal", "General Fitness"),
            duration_min=int(arguments.get("duration_min", 50)),
            fitness_level=arguments.get("fitness_level", "Intermediate"),
            equipment=list(arguments.get("equipment", [])),
            target_muscles=list(arguments.get("target_muscles", [])) or ["Full Body"],
        )
        return generate_session(sp)
    if name == "generate_training_program":
        params = {
            "weeks": int(arguments.get("weeks", 4)),
            "days_per_week": int(arguments.get("days_per_week", 3)),
            "goal": arguments.get("goal", "General Fitness"),
            "duration_min": int(arguments.get("duration_min", 50)),
            "fitness_level": arguments.get("fitness_level", "Intermediate"),
            "equipment": list(arguments.get("equipment", [])),
        }
        return generate_plan(params)
    if name == "generate_meal_plan":
        return _build_meal_plan(arguments)
    return {"error": f"Unknown tool {name}"}


def _build_meal_plan(args: Dict[str, Any]) -> Dict[str, Any]:
    days = max(1, int(args.get("days", 3)))
    kcal = int(args.get("calories", 2200))
    meals_per_day = min(6, max(2, int(args.get("meals_per_day", 3))))
    protein_g = args.get("protein_g")
    fat_g = args.get("fat_g")
    carbs_g = args.get("carbs_g")
    diet = (args.get("diet") or "balanced").lower()

    # Compute macros if not specified
    if not (protein_g and fat_g and carbs_g):
        # defaults: ~30% protein, 30% fat, 40% carbs for balanced
        p_ratio, f_ratio, c_ratio = (0.3, 0.3, 0.4)
        if "keto" in diet:
            p_ratio, f_ratio, c_ratio = (0.25, 0.7, 0.05)
        if "high" in diet and "protein" in diet:
            p_ratio, f_ratio, c_ratio = (0.35, 0.25, 0.40)
        protein_g = protein_g or round((kcal * p_ratio) / 4)
        fat_g = fat_g or round((kcal * f_ratio) / 9)
        carbs_g = carbs_g or round((kcal * c_ratio) / 4)

    # Split per meal
    p_pm = round(protein_g / meals_per_day)
    f_pm = round(fat_g / meals_per_day)
    c_pm = round(carbs_g / meals_per_day)
    cal_pm = round(kcal / meals_per_day)

    meal_names = ["Breakfast", "Lunch", "Dinner", "Snack", "Supper", "Snack 2"]
    sample_items = {
        "balanced": [
            "Greek yogurt with berries and honey",
            "Chicken, rice, and steamed vegetables",
            "Salmon with quinoa and asparagus",
            "Oats with whey and banana",
            "Beef stir-fry with mixed veggies",
        ],
        "vegetarian": [
            "Tofu scramble with spinach and toast",
            "Lentil curry with brown rice",
            "Chickpea salad with feta and olive oil",
            "Oats, almond milk, chia seeds, berries",
            "Paneer tikka with salad",
        ],
        "vegan": [
            "Tofu scramble with spinach",
            "Chickpea and quinoa bowl",
            "Tempeh stir-fry with veggies",
            "Overnight oats with almond milk",
            "Lentil bolognese on whole wheat pasta",
        ],
        "keto": [
            "Scrambled eggs with avocado",
            "Grilled chicken salad with olive oil",
            "Salmon with broccoli and butter",
            "Greek salad with olives and feta",
            "Bunless burger with cheese and greens",
        ],
        "high-protein": [
            "Egg white omelet + oats",
            "Turkey rice bowl",
            "Cottage cheese + fruit",
            "Protein shake + nuts",
            "Steak, potatoes, green beans",
        ],
    }
    key = "balanced"
    for k in sample_items.keys():
        if k in diet:
            key = k
            break

    out_days: List[Dict[str, Any]] = []
    for d in range(1, days + 1):
        meals = []
        for m in range(meals_per_day):
            meals.append({
                "name": meal_names[m],
                "calories": cal_pm,
                "protein_g": p_pm,
                "carbs_g": c_pm,
                "fat_g": f_pm,
                "items": [sample_items[key][(d + m) % len(sample_items[key])]],
            })
        out_days.append({"day": d, "meals": meals, "totals": {"calories": kcal, "protein_g": protein_g, "carbs_g": carbs_g, "fat_g": fat_g}})

    return {"days": out_days, "calories": kcal, "meals_per_day": meals_per_day, "diet": diet}


def ai_respond(messages: List[Dict[str, str]], max_tool_loops: int = 2) -> Dict[str, Any]:
    """
    Call OpenAI with tools enabled. Returns dict with keys:
    - role: 'assistant'
    - text: assistant content
    - tool_runs: list of {name, arguments, result}
    - raw: raw API response (if available)
    """
    try:
        from openai import OpenAI  # type: ignore
    except Exception as e:  # pragma: no cover
        return {"role": "assistant", "text": f"AI unavailable: {e}", "tool_runs": [], "raw": None}

    client = OpenAI(api_key=getattr(settings, "OPENAI_API_KEY", None))
    if not getattr(settings, "OPENAI_API_KEY", None):
        return {"role": "assistant", "text": "OpenAI API key not configured.", "tool_runs": [], "raw": None}

    tool_runs: List[Dict[str, Any]] = []
    augmented = [{"role": "system", "content": SYSTEM_PROMPT}] + messages
    tools = _tool_defs()

    result_text = ""
    raw_last: Optional[Dict[str, Any]] = None

    for _ in range(max_tool_loops + 1):
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=augmented,
            tools=tools,
            temperature=0.3,
        )
        raw_last = resp.model_dump()  # type: ignore
        choice = resp.choices[0]
        msg = choice.message
        if msg.tool_calls:
            # Execute tools and append results
            for call in msg.tool_calls:
                name = call.function.name
                args = json.loads(call.function.arguments or "{}")
                result = _run_tool(name, args)
                tool_runs.append({"name": name, "arguments": args, "result": result})
                augmented.append({
                    "role": "tool",
                    "tool_call_id": call.id,
                    "name": name,
                    "content": json.dumps(result),
                })
            continue
        # No more tools; capture final text
        result_text = (msg.content or "").strip()
        break

    return {"role": "assistant", "text": result_text, "tool_runs": tool_runs, "raw": raw_last}
