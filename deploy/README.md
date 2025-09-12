Staging/Prod quickstart

1) docker compose
- Put TLS certs in `./certs/fullchain.pem` and `./certs/privkey.pem`.
- Configure `.env` or environment for `SECRET_KEY`, `ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS`, and `DATABASE_URL`.
- Start services: `docker compose -f docker-compose.staging.yml up -d`.

2) nginx
- Terminates TLS and forwards to `web:8000`.
- Sends `X-Forwarded-Proto: https` so Django trusts HTTPS (see `SECURE_PROXY_SSL_HEADER`).
- Adds HSTS header; confirm `SECURE_*` flags in `settings_prod.py`.

3) CORS
- Lock to your frontend origins using `CORS_ALLOWED_ORIGINS` environment variable (comma-separated URLs).

4) Postgres
- `DATABASE_URL=postgres://coach:coach@db:5432/coach` in compose by default.
- Data persists in the `pgdata` volume.

