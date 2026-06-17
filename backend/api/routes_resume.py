from fastapi import APIRouter, UploadFile, File, HTTPException
from db.database import create_session, save_profile
from resume_parser.extractor import extract_text_from_pdf
from agents.resume_agent import resume_agent

router = APIRouter()


@router.post("/resume/upload")
async def upload_resume(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    resume_text = extract_text_from_pdf(file_bytes)
    if len(resume_text.strip()) < 20:
        raise HTTPException(
            status_code=422,
            detail="Could not extract readable text from this PDF. Try a different file.",
        )

    session_id = create_session()

    result = await resume_agent.run(resume_text)

    save_profile(session_id, resume_text, result.output)

    return {
        "session_id": session_id,
        "parsed_profile": result.output,
        "confidence": result.confidence,
        "reasoning": result.reasoning,
        "assumptions": result.assumptions,
        "missing_data": result.missing_data,
    }