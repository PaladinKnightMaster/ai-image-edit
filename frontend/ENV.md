# Frontend Environment Variables

This file explains the frontend env vars used by the Next.js UI.

## Where to set values

- Copy `frontend/.env.example` to `frontend/.env.local`
- Restart the frontend dev server after changes

## Variables

- `NEXT_PUBLIC_BACKEND_URL` base URL for the backend API (default `http://localhost:8000`)

Example:
```
NEXT_PUBLIC_BACKEND_URL=http://192.168.1.50:8000
```
