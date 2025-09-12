from .settings import *  # noqa
import os

# Production-safe overrides
DEBUG = False

SECRET_KEY = os.environ.get('SECRET_KEY') or SECRET_KEY

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',') if os.environ.get('ALLOWED_HOSTS') else ALLOWED_HOSTS

SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = int(os.environ.get('SECURE_HSTS_SECONDS', '31536000'))  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = False

# Trust proxy headers (nginx/ALB)
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True

# Static files (collectstatic)
STATIC_ROOT = BASE_DIR / 'static'

# CORS restrict (set CORS_ALLOWED_ORIGINS csv in env)
cors = os.environ.get('CORS_ALLOWED_ORIGINS')
if cors:
    CORS_ALLOW_ALL_ORIGINS = False
    CORS_ALLOWED_ORIGINS = [x.strip() for x in cors.split(',') if x.strip()]

# DRF throttles: keep defaults from base; allow env overrides
if 'DRF_USER_RATE' in os.environ:
    REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']['user'] = os.environ['DRF_USER_RATE']
if 'DRF_ANON_RATE' in os.environ:
    REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']['anon'] = os.environ['DRF_ANON_RATE']

# Database: allow DATABASE_URL=postgres://user:pass@host:5432/dbname
db_url = os.environ.get('DATABASE_URL')
if db_url:
    from urllib.parse import urlparse
    u = urlparse(db_url)
    if u.scheme.startswith('postgres'):
        DATABASES['default'] = {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': u.path.lstrip('/'),
            'USER': u.username,
            'PASSWORD': u.password,
            'HOST': u.hostname,
            'PORT': str(u.port or ''),
            'CONN_MAX_AGE': 60,
            'OPTIONS': {},
        }
