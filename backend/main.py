from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from db.database import init_db
from api import routes_session, routes_resume, routes_dashboard

app = FastAPI(title="CareerOS API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    init_db()

app.include_router(routes_session.router, prefix="/api", tags=["session"])
app.include_router(routes_resume.router, prefix="/api", tags=["resume"])
app.include_router(routes_dashboard.router, prefix="/api", tags=["dashboard"])

@app.get("/")
def root():
    return {"status": "CareerOS API running"}