import fitz  # PyMuPDF
import pdfplumber
from io import BytesIO


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Extract text from a PDF resume using PyMuPDF first,
    falling back to pdfplumber if extraction yields too little text.
    """
    text = _extract_with_pymupdf(file_bytes)

    if len(text.strip()) < 50:
        text = _extract_with_pdfplumber(file_bytes)

    return text.strip()


def _extract_with_pymupdf(file_bytes: bytes) -> str:
    text_parts = []
    with fitz.open(stream=file_bytes, filetype="pdf") as doc:
        for page in doc:
            text_parts.append(page.get_text())
    return "\n".join(text_parts)


def _extract_with_pdfplumber(file_bytes: bytes) -> str:
    text_parts = []
    with pdfplumber.open(BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
    return "\n".join(text_parts)