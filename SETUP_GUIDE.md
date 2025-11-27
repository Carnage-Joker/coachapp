# Dig Deep Fitness Platform - Setup Guide

## Overview

Dig Deep Fitness Platform (DDFP) is a premium fitness platform designed for personal trainers and clients. It features AI-powered workout generation, client management, progress tracking, and more.

## Stack

- **Backend**: Django 5 + Django REST Framework
- **Database**: SQLite (dev) → PostgreSQL (production)
- **Frontend**: Next.js 15 (App Router, TypeScript, Tailwind CSS)
- **Authentication**: JWT (Simple JWT)
- **Exercise Database**: CSV with 60+ exercises

## Prerequisites

- Python 3.12+
- Node.js 18+
- npm or yarn

## Backend Setup

### 1. Create Virtual Environment

```bash
cd coachapp
python -m venv .venv
```

### 2. Activate Virtual Environment

**Windows:**
```bash
.\.venv\Scripts\activate
```

**Linux/Mac:**
```bash
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run Migrations

```bash
python manage.py migrate
```

### 5. Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

### 6. Run Development Server

```bash
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000`

## Frontend Setup

### 1. Navigate to Frontend Directory

```bash
cd frontend
```

### 2. Install Dependencies

```bash
npm install
```

### 3. Create Environment File

```bash
cp .env.local.example .env.local
```

Edit `.env.local` to set your API base URL:
```
NEXT_PUBLIC_API_BASE=http://127.0.0.1:8000
```

### 4. Run Development Server

```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

## Running Both Servers (Recommended)

From the root `coachapp/` directory:

```bash
npm run dev
```

This will start both the Django backend and Next.js frontend concurrently.

## Key Features

### 1. Client Management
- Create and manage client profiles
- Track client goals, equipment, injuries
- View client statistics

### 2. Workout Generation
- AI-powered workout plan generation
- Based on client profile, equipment, goals
- Respects injury constraints and preferences
- 60+ exercises with detailed instructions

### 3. Exercise Library
- Browse all available exercises
- Filter by equipment, movement pattern, skill level
- View coaching cues and contraindications
- Home-friendly and outdoor-friendly indicators

### 4. Authentication
- JWT-based authentication
- Secure login and registration
- Token refresh mechanism
- Protected routes

## API Endpoints

### Authentication
- `POST /api/auth/token/` - Obtain JWT token
- `POST /api/auth/token/refresh/` - Refresh token
- `POST /api/auth/register/` - Register new user
- `POST /api/auth/logout/` - Logout (blacklist token)
- `GET /api/auth/me/` - Get current user

### Clients
- `GET /api/clients/` - List clients (authenticated)
- `POST /api/clients/` - Create client
- `GET /api/clients/<uuid>/` - Get client details
- `PUT/PATCH /api/clients/<uuid>/` - Update client
- `DELETE /api/clients/<uuid>/` - Delete client
- `GET /api/clients/<uuid>/plan/` - Generate workout plan
- `GET /api/clients/<uuid>/plan/?save=true` - Generate and save plan

### Workouts
- `POST /api/workouts/generate/` - Generate single workout
- `POST /api/workouts/plan/` - Generate full training plan

### Consults
- `GET/POST /api/consults/` - List/create consultations
- `GET/POST /api/consults/<id>/messages/` - Chat messages
- `POST /api/consults/<id>/voice/` - Voice interaction
- `POST /api/consults/<id>/generate/` - Generate assessment

### Emails
- `POST /api/emails/send/` - Send email
- `GET /api/emails/logs/` - View email logs

### Bookings
- Booking system endpoints (coming soon)

## Exercise Database

The exercise database is located at `coachapp/data/exercise_db.csv` with the following schema:

- Exercise ID
- Exercise
- Compound (TRUE/FALSE)
- Movement Pattern
- Default Reps, Sets, Rest
- Unilateral/Bilateral
- Equipment
- Location Suitability
- Space Needed
- Impact Level
- Injury-Friendly flags (Knee, Shoulder, Back)
- Skill Level
- Target RPE
- Tempo
- Metcon Score
- Contraindications
- Coaching Cues
- Video URL
- Tags
- Body Region
- Primary Muscle Group
- Plane of Motion
- Force Vector
- Load Type
- Home/Outdoor-Friendly flags
- Warm-Up Category
- Estimated Time per Set

## Configuration

### Backend (`coachapp/settings.py`)

Key settings:
- `SECRET_KEY` - Change in production
- `DEBUG` - Set to False in production
- `ALLOWED_HOSTS` - Add your domain
- `CORS_ALLOW_ALL_ORIGINS` - Disable in production
- Database settings for PostgreSQL

### Frontend (`frontend/.env.local`)

```
NEXT_PUBLIC_API_BASE=http://127.0.0.1:8000
```

Change to your production API URL when deploying.

## Testing

### Backend Tests

```bash
python manage.py test
```

Current tests:
- Authentication flow (login, refresh, logout)
- Client ownership and isolation
- Anonymous access restrictions

### Frontend Build

```bash
cd frontend
npm run build
```

## Deployment

### Backend (Django)

1. Set environment variables:
   - `SECRET_KEY`
   - `DEBUG=False`
   - `ALLOWED_HOSTS`
   - Database credentials (PostgreSQL)

2. Collect static files:
   ```bash
   python manage.py collectstatic
   ```

3. Run migrations:
   ```bash
   python manage.py migrate
   ```

4. Use gunicorn or similar WSGI server:
   ```bash
   gunicorn coachapp.wsgi:application
   ```

### Frontend (Next.js)

1. Build the application:
   ```bash
   npm run build
   ```

2. Start production server:
   ```bash
   npm start
   ```

Or deploy to Vercel, Netlify, or similar platforms.

## Troubleshooting

### Database Issues

If you encounter SQLite errors with arrays:
- Ensure you're using `models.JSONField` for lists in development
- Migrate to PostgreSQL `ArrayField` only in production

### CORS Issues

If frontend can't connect to backend:
- Ensure `django-cors-headers` is installed
- Add frontend URL to `CORS_ALLOWED_ORIGINS` in settings
- Or enable `CORS_ALLOW_ALL_ORIGINS=True` in development

### Frontend Build Errors

If Tailwind CSS errors occur:
- Ensure `@tailwindcss/postcss` is installed
- Check `postcss.config.js` configuration
- Verify `tailwind.config.js` paths

## Support

For issues, feature requests, or questions, please open an issue on GitHub.

## License

[Your License Here]
