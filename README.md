# Dig Deep Fitness Platform (coachapp)

Dev runbook (Windows):

- Backend
  - cd coachapp
  - .\.venv\Scripts\activate
  - python manage.py migrate
  - python manage.py runserver

- Frontend
  - cd coachapp\frontend
  - copy .env.local.example .env.local
  - npm run dev

Key endpoints

- Auth (JWT): `POST /api/auth/token/`, `POST /api/auth/token/refresh/`
- Clients: `GET/POST /api/clients/`, `GET /api/clients/<uuid>/`, `GET /api/clients/<uuid>/plan/?save=true`
- Consults: `GET/POST /api/consults/`, `GET/POST /api/consults/<id>/messages/`, `POST /api/consults/<id>/voice/?tts=true`, `POST /api/consults/<id>/generate/`
- Workouts: `POST /api/workouts/generate/`, `POST /api/workouts/plan/`
- Emails: `POST /api/emails/send/`, `GET /api/emails/logs/`

Styling

- Tailwind theme configured in `frontend/tailwind.config.ts` with brand CSS variables in `frontend/src/app/globals.css` (palette inspired by https://ddfp.my.canva.site/).
