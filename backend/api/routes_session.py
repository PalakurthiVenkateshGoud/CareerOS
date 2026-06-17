from fastapi import APIRouter
from db.database import create_session

router = APIRouter()


@router.post("/session")
async def new_session():
    session_id = create_session()
    return {"session_id": session_id}