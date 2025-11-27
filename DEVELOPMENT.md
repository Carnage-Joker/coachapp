# Development Guide

This guide is for developers working on the Dig Deep Fitness Platform.

## Development Principles

1. **Be surgical**: Make precise, minimal changes
2. **Prefer action over questions**: State assumptions and proceed
3. **Production-ready code**: No placeholders or TODOs
4. **Respect constraints**: SQLite in dev, Postgres in prod
5. **Follow the checklist**: Models → Serializers → URLs → Views → UI → Tests

## Code Style

### Python/Django

- Follow PEP 8
- Use type hints for non-trivial functions
- Black formatting (line length 88)
- Use Django conventions (ModelViewSet, router-based URLs)
- Nested creates in parent serializer `create()` method

Example:
```python
from typing import Dict, Any

def normalize_client_profile(client: Client) -> Dict[str, Any]:
    """Build generator-ready profile from client data."""
    profile = {
        "equipment_allowed": [...],
        "location": client.primary_location,
        # ...
    }
    return profile
```

### TypeScript/React

- Use App Router (not Pages Router)
- Client components must begin with `'use client'`
- Strong types for payloads - avoid `any`
- Never inline try/catch inside JSX
- Keep side effects in handlers

Example:
```typescript
'use client'

import { useState } from 'react'

interface ClientData {
  first_name: string
  last_name: string
  // ...
}

export default function IntakePage() {
  const [data, setData] = useState<ClientData>({
    first_name: '',
    last_name: '',
  })
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      // API call
    } catch (err) {
      // Handle error
    }
  }
  
  return <form onSubmit={handleSubmit}>...</form>
}
```

## Database

### Development (SQLite)

- Use `models.JSONField` for arrays/lists
- No `ArrayField` in development migrations
- Lightweight, file-based, good for local dev

### Production (PostgreSQL)

- Can use `ArrayField` with dedicated migration
- Better performance and features
- Connection pooling, full-text search

### Migrations

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Check for issues
python manage.py check
```

## API Development

### Adding a New Endpoint

1. **Model** (if needed): Define in `models.py`
2. **Serializer**: Create in `serializers.py`
3. **ViewSet**: Create in `views.py`
4. **URLs**: Register in `urls.py`
5. **Test**: Add tests in `tests.py`

Example ViewSet:
```python
from rest_framework import viewsets, permissions
from .models import MyModel
from .serializers import MySerializer

class MyViewSet(viewsets.ModelViewSet):
    serializer_class = MySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return MyModel.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
```

### URL Registration

```python
from rest_framework.routers import DefaultRouter
from .views import MyViewSet

router = DefaultRouter()
router.register('mymodel', MyViewSet, basename='mymodel')

urlpatterns = [
    path('', include(router.urls)),
]
```

## Frontend Development

### Adding a New Page

1. Create directory: `frontend/src/app/mypage/`
2. Create `page.tsx` with default export
3. Add navigation links
4. Style with Tailwind CSS

### API Calls

Always use the environment variable for API base:
```typescript
const apiBase = process.env.NEXT_PUBLIC_API_BASE || 'http://127.0.0.1:8000'
const token = localStorage.getItem('access_token')

const response = await fetch(`${apiBase}/api/endpoint/`, {
  method: 'GET',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json',
  },
})
```

### Styling

Use Tailwind utility classes:
```tsx
<div className="bg-white rounded-lg shadow-md p-6">
  <h2 className="text-2xl font-bold text-gray-900 mb-4">Title</h2>
  <button className="bg-brand-600 text-white px-4 py-2 rounded-lg hover:bg-brand-700 transition">
    Action
  </button>
</div>
```

Brand colors are defined in `tailwind.config.js`:
- `brand-50` to `brand-900`

## Testing

### Backend Tests

Create tests in `tests.py`:
```python
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient

class MyTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='test',
            password='testpass123'
        )
        
    def test_authenticated_access(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/endpoint/')
        self.assertEqual(response.status_code, 200)
```

Run tests:
```bash
python manage.py test
python manage.py test app_name.tests.TestClass
python manage.py test app_name.tests.TestClass.test_method
```

### Frontend Testing

Build to check for TypeScript errors:
```bash
cd frontend
npm run build
```

## Exercise Database

The canonical CSV is at `coachapp/data/exercise_db.csv`.

### Adding Exercises

1. Edit the CSV file
2. Follow the exact column headers
3. Use canonical values for enums:
   - Space: `Small|Medium|Large`
   - Impact: `Low|Moderate|High`
   - Skill Level: `Beginner|Intermediate|Advanced`
   - Location: `Home|Gym|Outdoor`
4. Set boolean fields as `TRUE|FALSE`

### Movement Patterns (Fixed List)

- Squat
- Hinge
- Horizontal Push
- Horizontal Pull
- Vertical Push
- Vertical Pull
- Lunge
- Core – Brace/Anti-Extension
- Carry/Gait
- Jump/Power
- Conditioning

## Workout Generation

The generator (`clients/services/generator.py`):

1. Loads exercises from CSV
2. Filters by equipment, location, skill level
3. Respects injury constraints
4. Balances movement patterns
5. Manages time budgets
6. Ensures pull coverage
7. Applies progressive overload

### Customizing Generation

Modify `_pick_exercises_from_csv()` to:
- Adjust pattern priorities
- Change time allocation
- Modify selection logic
- Add new filtering criteria

## Environment Variables

### Backend

Set in `coachapp/settings.py` or environment:
- `SECRET_KEY` - Django secret key (required in prod)
- `DEBUG` - Debug mode (False in prod)
- `ALLOWED_HOSTS` - Comma-separated hosts
- `DATABASE_URL` - PostgreSQL connection string (prod)
- `CORS_ALLOWED_ORIGINS` - Frontend URLs

### Frontend

Set in `frontend/.env.local`:
```
NEXT_PUBLIC_API_BASE=http://127.0.0.1:8000
```

## Common Issues

### "near '[]': syntax error"

You used `ArrayField` on SQLite. Replace with `JSONField`:
```python
# Bad (SQLite)
tags = models.ArrayField(models.CharField(max_length=50))

# Good (SQLite)
tags = models.JSONField(default=list)
```

### "client field is required" on nested POST

Mark nested serializer's client field as read-only:
```python
class NestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = NestedModel
        exclude = ('client',)
```

### Next.js 404 on page

- Ensure file at correct path: `frontend/src/app/page/page.tsx`
- File must default-export a component
- Fix TypeScript errors (run `npm run build`)

### Cannot read properties of null

Event target used after `await`. Capture first:
```typescript
const handleSubmit = async (e: React.FormEvent) => {
  const form = e.currentTarget  // Capture before await
  e.preventDefault()
  
  await apiCall()
  
  form.reset()  // Use captured reference
}
```

## Git Workflow

1. Create feature branch: `git checkout -b feature/my-feature`
2. Make changes in small, logical commits
3. Test thoroughly before committing
4. Push and create pull request
5. Address review comments
6. Merge when approved

## Code Review Checklist

- [ ] Code follows style guidelines
- [ ] No console.log or print statements
- [ ] Error handling is comprehensive
- [ ] User input is validated
- [ ] SQL injection protected (use ORM)
- [ ] XSS protected (React escapes by default)
- [ ] Authentication/authorization checked
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] No secrets in code

## Performance

### Backend

- Use `select_related()` and `prefetch_related()` for related objects
- Add database indexes for frequently queried fields
- Use pagination for large result sets
- Cache expensive computations

### Frontend

- Use Next.js Image component for images
- Lazy load components with `dynamic()`
- Minimize bundle size (check with `npm run build`)
- Debounce search inputs

## Deployment

See [SETUP_GUIDE.md](./SETUP_GUIDE.md) for deployment instructions.

### Checklist

Backend:
- [ ] `DEBUG=False`
- [ ] `SECRET_KEY` set from environment
- [ ] `ALLOWED_HOSTS` configured
- [ ] PostgreSQL database configured
- [ ] Static files collected
- [ ] Migrations run
- [ ] HTTPS enabled
- [ ] Sentry configured (optional)

Frontend:
- [ ] `NEXT_PUBLIC_API_BASE` points to production API
- [ ] Build succeeds (`npm run build`)
- [ ] Environment variables set
- [ ] CDN configured (optional)

## Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [DRF Documentation](https://www.django-rest-framework.org/)
- [Next.js Documentation](https://nextjs.org/docs)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)

## Getting Help

- Check existing issues on GitHub
- Review custom_instructions.md
- Ask in team chat
- Create detailed issue with:
  - Steps to reproduce
  - Expected vs actual behavior
  - Error messages
  - Environment details
