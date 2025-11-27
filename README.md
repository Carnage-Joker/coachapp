# Dig Deep Fitness Platform (coachapp)

A premium fitness platform designed for personal trainers and clients to maximize progress through AI-powered workout generation, comprehensive client management, and personalized training programs.

## 🌟 Features

### Core Features
- **AI-Powered Workout Generation**: Automatically generate personalized weekly workout plans based on client profiles
- **Client Management**: Comprehensive client intake and profile management
- **Exercise Library**: 60+ exercises with detailed instructions, coaching cues, and video references
- **Progress Tracking**: Monitor client progress and adjust programs accordingly
- **Injury Management**: Respect injury constraints and generate safe, effective workouts
- **Equipment Flexibility**: Adapt workouts to available equipment (home, gym, outdoor)

### Advanced Features
- **JWT Authentication**: Secure user authentication and authorization
- **Skill-Based Exercise Selection**: Match exercises to client skill level
- **Progressive Overload**: Automatically increase difficulty across training blocks
- **Movement Pattern Balancing**: Ensure balanced weekly programming
- **Custom Equipment Profiles**: Track what equipment clients have access to
- **Goal-Based Programming**: Generate workouts aligned with specific fitness goals

## 🚀 Quick Start

See [SETUP_GUIDE.md](./SETUP_GUIDE.md) for detailed setup instructions.

### Backend Quick Start

```bash
cd coachapp
python -m venv .venv
.\.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### Frontend Quick Start

```bash
cd coachapp/frontend
npm install
cp .env.local.example .env.local
npm run dev
```

### Run Both Servers

From the root `coachapp/` directory:

```bash
npm run dev
```

## 📚 Documentation

- [Setup Guide](./SETUP_GUIDE.md) - Complete setup instructions
- [Custom Instructions](./chatgpt/custom_instructions.md) - Development guidelines and conventions
- [API Documentation](#api-endpoints) - Below

## 🛠 Tech Stack

- **Backend**: Django 5.2.5 + Django REST Framework 3.16
- **Frontend**: Next.js 15 (App Router) + TypeScript + Tailwind CSS
- **Database**: SQLite (dev) → PostgreSQL (prod)
- **Authentication**: JWT (djangorestframework-simplejwt)
- **Styling**: Tailwind CSS with custom brand colors

## 📋 API Endpoints

### Authentication
- `POST /api/auth/token/` - Obtain JWT token
- `POST /api/auth/token/refresh/` - Refresh token
- `POST /api/auth/register/` - Register new user
- `GET /api/auth/me/` - Get current user
- `POST /api/auth/logout/` - Logout

### Clients
- `GET /api/clients/` - List all clients (scoped to user)
- `POST /api/clients/` - Create new client
- `GET /api/clients/<uuid>/` - Get client details
- `PATCH /api/clients/<uuid>/` - Update client
- `GET /api/clients/<uuid>/plan/` - Generate workout plan
- `GET /api/clients/<uuid>/plan/?save=true` - Generate and save plan

### Workouts
- `POST /api/workouts/generate/` - Generate single workout session
- `POST /api/workouts/plan/` - Generate full training plan

### Additional Features
- Consultation system with AI assistant
- Email logging and management
- Booking system (in development)
- Template management
- Progress tracking

## 💾 Exercise Database

60+ exercises covering:
- **Movement Patterns**: Squat, Hinge, Push, Pull, Lunge, Core, Carry, Power, Conditioning
- **Equipment**: Bodyweight, Dumbbells, Kettlebells, Barbells, Rings, Machines, Bands
- **Skill Levels**: Beginner, Intermediate, Advanced
- **Metadata**: Coaching cues, contraindications, video URLs, time estimates

## 🎯 Client Profile

Client profiles include:
- Demographics (age, height, weight, training age)
- Training logistics (location, space, equipment, time availability)
- Goals (strength, hypertrophy, fat loss, conditioning, etc.)
- Injury history and constraints
- Movement preferences and dislikes
- RPE familiarity and target intensity

## 🏋️ Workout Generation

The workout generator:
1. Loads exercise database from CSV
2. Filters exercises based on client profile
3. Balances movement patterns across the week
4. Respects time budgets and equipment constraints
5. Honors injury-friendly requirements
6. Ensures pull movement coverage
7. Applies progressive overload across blocks
8. Adds appropriate warm-ups

## 🧪 Testing

Run backend tests:
```bash
python manage.py test
```

Current test coverage:
- Authentication flow (login, refresh, logout, blacklist)
- Client ownership and isolation
- Anonymous access restrictions

## 🎨 Frontend Pages

- `/` - Landing page with features
- `/login` - User authentication
- `/register` - New user registration
- `/dashboard` - Coach dashboard with client overview
- `/intake` - Client intake form
- `/plans` - Workout plan generator and viewer
- `/exercises` - Exercise library browser

## 🔐 Security

- JWT-based authentication with token blacklisting
- User-scoped data access (coaches only see their clients)
- Rate limiting on authentication endpoints
- CORS configuration for API access
- Password validation and hashing

## 📊 Data Models

### Core Models
- **Client**: Core client information and training logistics
- **ClientInjury**: Injury tracking
- **ClientPreference**: Exercise/movement preferences
- **ClientEquipment**: Available equipment
- **ClientProfile**: Normalized, generator-ready profile
- **ClientBlock**: Saved workout plans

### Supporting Models
- **Consult**: Consultation sessions
- **Message**: Chat messages for consultations
- **Assessment**: Generated assessments
- **EmailLog**: Email tracking

## 🔄 Workflow

1. **Coach Registration**: Create coach account
2. **Client Intake**: Fill out comprehensive client form
3. **Profile Normalization**: System processes client data
4. **Plan Generation**: AI generates personalized workout plan
5. **Plan Review**: Coach reviews and can modify
6. **Plan Delivery**: Client receives workout program
7. **Progress Tracking**: Monitor adherence and progress
8. **Progressive Overload**: System adjusts difficulty over time

## 📱 Mobile Support

The frontend is fully responsive and works on:
- Desktop browsers
- Tablets
- Mobile phones

## 🚧 Roadmap

- [ ] PDF/CSV export for workout plans
- [ ] Client portal for workout viewing
- [ ] Exercise video demonstrations
- [ ] Progress photo tracking
- [ ] Advanced analytics and charts
- [ ] Mobile app (React Native)
- [ ] Wearable device integration
- [ ] Group workout features
- [ ] Meal planning integration
- [ ] Payment processing (Stripe)

## 📄 License

[Your License Here]

## 🤝 Contributing

Contributions are welcome! Please read the contributing guidelines first.

## 📧 Support

For support, email support@digdeepfitness.com or open an issue on GitHub.

---

**Built with ❤️ for coaches and athletes worldwide**
