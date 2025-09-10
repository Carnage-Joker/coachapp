# Dig Deep Fitness Platform (DDFP) — Custom Instructions

**Goal:** Intake clients → normalize their profile → auto-generate time-boxed, equipment-aware weekly workouts from a rich exercise database.

**desired outcomes:** Improved client fitness levels, increased adherence to workout plans, and a more personalized training experience.

**new features:** Enhanced exercise selection algorithms, gamified progress tracking, client-specific workout recommendations, client management tools, group workout features, group workout generation improved user interface for workout customization, and integration with wearable fitness devices.

**Stack:** Django 5 + DRF, SQLite (dev) → Postgres (prod), Next.js 15 (App Router, TypeScript, Tailwind), CSV/XLSX exercise DB.

---

## 1) How ChatGPT should help (meta-rules)

- Be surgical. When code is requested, output exact files with paths or unified diffs. No placeholders; production-ready snippets.
- Prefer action over questions. Ask only when ambiguity truly blocks progress; otherwise state assumptions.
- Show commands. Always include **Windows-friendly** commands and any env vars.
- Respect constraints. Dev DB is SQLite → use `models.JSONField` for lists in dev; don’t introduce Postgres-only `ArrayField` in dev migrations.
- Checklists first. For new features: **models → serializers → urls → views → UI → tests → run**.
- Explainers inline. 1–2 lines of rationale; avoid long essays.
- On errors: lead with the minimal patch, then root cause.

---

## 2) Local dev runbook

**Backend (from `coachapp/`):**
..venv\Scripts\activate
python manage.py check
python manage.py makemigrations
python manage.py migrate
python manage.py runserver

javascript
Copy
Edit

**Frontend (from `coachapp/frontend/`):**
npm run dev

markdown
Copy
Edit

**API base (frontend):** `frontend/.env.local`
NEXT_PUBLIC_API_BASE=http://127.0.0.1:8000

pgsql
Copy
Edit

Optional root runner (`coachapp/package.json`) can offer `npm run dev` to start both servers via `concurrently`.

---

## 3) Data model (current)

- **Client** → core demographics & logistics (days/week, session length, space, impact, location).
- **ClientInjury** → region, severity, active.
- **ClientPreference** → `kind ∈ {'Exercise'|'Movement Pattern'}`, value, sentiment.
- **ClientEquipment** → location, category, details JSON.
- **ClientProfile** → derived JSON; generator-ready filters & weights.

**Signals:** on `post_save(Client)`, rebuild `ClientProfile.profile` via normalizer.

**SQLite note:** use `models.JSONField` for arrays in dev; migrate to Postgres `ArrayField` only in production with a dedicated migration.

---

## 4) Exercise DB — canonical schema

**Columns (keep headers exact):**

Exercise ID, Exercise, Compound, Movement Pattern, Default Reps, Default Sets, Default Rest (s),
Unilateral/Bilateral, Equipment, Location Suitability, Space Needed, Impact Level, Knee-Friendly,
Shoulder-Friendly, Back-Friendly, Skill Level, Target RPE, Tempo, Metcon Score (1-5),
Contraindications, Coaching Cues, Video URL, Tags, Body Region, Primary Muscle Group,
Plane of Motion, Force Vector, Load Type, Home-Friendly, Outdoor-Friendly, Warm-Up Category,
Est. Time/Set

pgsql
Copy
Edit

**Canonical values:**
- **Space Needed:** `Small|Medium|Large`
- **Impact Level:** `Low|Moderate|High`
- `*-Friendly:` `TRUE|FALSE` (string or bool; be consistent)
- **Compound:** `TRUE|FALSE`
- **Unilateral/Bilateral:** `Unilateral|Bilateral|Both`
- **Skill Level:** `Beginner|Intermediate|Advanced`
- **Movement Pattern (fixed):** `Squat,Hinge,Horizontal Push,Horizontal Pull,Vertical Push,Vertical Pull,Lunge,Core – Brace/Anti-Extension,Carry/Gait,Jump/Power,Conditioning`
- **Equipment (align intake):** `Bodyweight,Dumbbells,Kettlebell,Barbell,Rings,Gym Equipment,Cable/Machine,Bands/Chains,Strongman,Med Ball,Cardio Machine`
- **Est. Time/Set:** seconds (numeric)

---

## 5) APIs (DRF)

- `POST /api/clients/` — create client. Nested arrays (`injuries`,`preferences`,`equipment`) accepted; nested serializers exclude `client` and are attached in `ClientSerializer.create()`.
- `GET /api/clients/` — list
- `GET /api/clients/<uuid>/` — detail
- `GET /api/clients/<uuid>/plan/` — build a week plan JSON using the CSV/XLSX DB and the ClientProfile.

**Common fixes:**
- *“client: This field is required”* on nested POST → nested serializers must `exclude=('client',)` or set `extra_kwargs={'client': {'read_only': True}}`.
- CORS in dev: `CORS_ALLOW_ALL_ORIGINS=True`.

---

## 6) Normalizer (profile shape)

```json
{
  "equipment_allowed": ["Bodyweight","Dumbbells","..."],
  "location": "Home|Gym|Outdoor",
  "space_max": "Small|Medium|Large",
  "impact_max": "Low|Moderate|High",
  "require_knee_friendly": true,
  "require_shoulder_friendly": false,
  "require_back_friendly": false,
  "movement_weights": {"Squat":1.3,"Hinge":1.3,"...":1.0},
  "days_per_week": 3,
  "session_length_min": 60,
  "target_rpe": "7-9",
  "skill_level": "Beginner|Intermediate|Advanced",
  "disliked_exercises": ["Burpee"],
  "liked_exercises": ["Goblet Squat"]
}
7) Generator (current behavior)
Load exercise DB from coachapp/data/exercise_db.(csv|xlsx).

Filter by equipment, space, impact, *-Friendly, and dislikes.

Assemble days_per_week using a balanced template (push/pull/hinge/squat/core), avoid duplicates, respect rough time budget (Default Sets × Est. Time/Set), respect client preferences, and respect client goals. Ensure each day's plan is varied and engaging, but first prioritize compound movements and overall muscle balance. Programs should be generated as if they were tailored for each individual client.

Output:

json
Copy
Edit
{
  "client": "<display name>",
  "plan": {
    "Day 1": [{"Exercise":"...","Movement Pattern":"...","Default Reps":"...","Default Sets":4,"..."}],
    "Day 2": [...]
  }
}
8) Frontend (Next.js)
Page: /intake renders <ClientIntakeForm/> (client component).

On save, fetch /api/clients/, then /api/clients/<id>/plan/ and display JSON preview.

Avoid React event staleness: capture const form = e.currentTarget before any await; call form.reset() after success.

Keep network base configurable via NEXT_PUBLIC_API_BASE.

9) Style & conventions
Python/Django

PEP8; use type hints where non-trivial; black formatting.

DRF: ModelViewSet + router. Nested create in parent serializer create().

SQLite dev → JSONField for arrays; Postgres prod may swap to ArrayField with a migration.

TypeScript/React

App Router; client components must begin with 'use client'.

Strong types for payloads; no any in public API shapes.

Never inline try/catch inside JSX; keep side effects in handlers.

Docs

When adding features, update this file and the main README with run commands and env vars.

10) Troubleshooting quickies
near "[]": syntax error on migrate → you used ArrayField on SQLite. Replace with JSONField, delete migration, re-makemigrations.

client field is required on nested POST → mark nested client read-only or exclude.

Next /intake 404 → page didn’t compile; fix TypeScript errors; ensure file at frontend/src/app/intake/page.tsx default-exports a component.

Cannot read properties of null (reading 'reset') → event target was used after await; capture const form = e.currentTarget first.

11) Definition of Done (feature)
DB migrations created and applied cleanly.

API endpoint(s) exposed and documented.

Frontend UI reachable via a page, not just a component.

Happy path tested end-to-end; errors return helpful JSON.

No TODO placeholders; commands provided for Windows shell.

12) Near-term roadmap
ClientBlock model to persist week plans; endpoints:

POST /api/clients/<id>/plan/save/

GET /api/clients/<id>/blocks/

Progressive overload across blocks; auto warm-ups from Warm-Up Category.

Skill-level gating of exercises; pull coverage guarantee per week.

Export (PDF/CSV); client portal view.

13) Prompting rules for ChatGPT (pasteable Custom Instructions)
About the project & user:

You are assisting on DDFP. Stack: Django 5 + DRF (SQLite dev → Postgres prod), Next.js 15, Tailwind, exercise DB in CSV/XLSX with the canonical headers above.

Primary objective: fast, runnable patches; minimal ceremony.

Dev OS: Windows; always include .\.venv\Scripts\activate and cmd.exe-friendly commands.

How to respond:

Provide exact file paths or unified diffs; runnable commands; short rationale.

Assume SQLite in dev; avoid Postgres-only features in migrations.

If ambiguity blocks progress, make one safe assumption and state it.

Keep answers concise; show code before prose; avoid placeholders.

For errors, give the minimal patch first, then root cause.

14) Quick scaffolds
Create a feature (template):

Models

Serializers

URLs

Views

UI (page + component)

Tests

Run: makemigrations, migrate, runserver, npm run dev

Windows commands (template):

bash
Copy
Edit
cd coachapp
.\.venv\Scripts\activate
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
cd frontend
npm run dev
yaml
Copy
Edit

---

### What next
- Commit this file so it lives in the repo:  
  `git add coachapp/chatgpt/custom_instructions.md && git commit -m "docs: add ChatGPT custom instructions"`
- Copy section **13) Prompting rules** into your ChatGPT **Custom Instructions** so future sessions follow the same playbook.
- When you want a new feature, ask in the format: “Add X → models, serializers, urls, views, UI, tests, run.” I’ll deliver a patch and the Windows commands to run it.