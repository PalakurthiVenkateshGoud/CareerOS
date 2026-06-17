# CareerOS — Deployment Guide

## Backend (Azure App Service)

1. Ensure `backend/requirements.txt` exists:

fastapi

uvicorn[standard]

pydantic-settings

openai

PyMuPDF

pdfplumber

2. Create an Azure App Service (Python 3.11 runtime).
3. Set environment variables in App Service Configuration:
   - `AZURE_OPENAI_ENDPOINT`
   - `AZURE_OPENAI_KEY`
   - `AZURE_OPENAI_DEPLOYMENT`
   - `DATABASE_URL` (keep as SQLite for hackathon, or migrate to Postgres)
4. Deploy via:

```bash
az webapp up --name careeros-api --resource-group <rg> --runtime "PYTHON:3.11"
```

5. Set startup command in App Service:

uvicorn main:app --host 0.0.0.0 --port 8000


## Frontend (Vercel)

1. Push `frontend/` to GitHub.
2. Import the repo into Vercel, set root directory to `frontend`.
3. Add environment variable:
   - `NEXT_PUBLIC_API_URL=https://<your-azure-app>.azurewebsites.net`
4. Deploy.

## CORS

Backend `main.py` already allows all origins (`allow_origins=["*"]`) for
hackathon simplicity. For production, restrict to the Vercel domain.

## Local Development

```bash
# Terminal 1 - backend
cd backend
uvicorn main:app --reload

# Terminal 2 - frontend
cd frontend
npm run dev
```