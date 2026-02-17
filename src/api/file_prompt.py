# src/api/file_prompt.py
from fastapi import APIRouter, Depends, HTTPException, Form
from sqlalchemy import select
from uuid import UUID
import logging
import io
import httpx
from PyPDF2 import PdfReader

from src.api.dependencies.supabase_dependencies import get_supabase_context
from src.models.user_files import UserFile
from src.LLM_Clients.factory import get_llm_client

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/files", tags=["file_prompt"])


async def extract_pdf_text(file_path: str, supabase) -> str:
    """
    Download PDF from Supabase and extract text using PyPDF2.
    """
    try:
        data = supabase.storage.from_("document").download(file_path)
        if data is None:
            return ""
        pdf_file = io.BytesIO(data)
        reader = PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text.strip()
    except Exception as e:
        logger.error(f"PDF extraction failed: {e}")
        return ""


@router.post("/ask")
async def ask_file(
    file_id: UUID = Form(...),
    prompt: str = Form(...),
    ctx = Depends(get_supabase_context)
):
    """
    Ask a question about a file already uploaded.
    Works with PDFs and images. Extracts text for PDFs before sending to LLM.
    """
    user = ctx["user"]
    db = ctx["db"]
    supabase = ctx["supabase"]

    # 1. Fetch file record
    stmt = select(UserFile).where(UserFile.id == file_id, UserFile.user_id == user.id)
    result = await db.execute(stmt)
    file_record = result.scalar_one_or_none()
    if not file_record:
        raise HTTPException(404, detail="File not found or access denied")

    public_url = file_record.public_url
    file_path = file_record.file_path
    mime_type = file_record.mime_type

    if not prompt.strip():
        raise HTTPException(400, detail="Prompt cannot be empty")

    # 2. Prepare LLM input
    llm_messages = []

    if "pdf" in mime_type:
        pdf_text = await extract_pdf_text(file_path, supabase)
        if not pdf_text:
            return {
                "file_id": str(file_id),
                "prompt": prompt,
                "answer": "(PDF text extraction failed; cannot generate answer)"
            }
        llm_messages.append({"type": "text", "text": pdf_text})
    else:
        # For images
        llm_messages.append({"type": "image_url", "image_url": {"url": public_url}})

    # Add user prompt
    full_prompt = (
        f"{prompt.strip()}\n\n"
        "Answer based **only** on the visible content in the file. "
        "Be precise, quote exact text/numbers, and avoid guessing."
    )
    llm_messages.append({"type": "text", "text": full_prompt})

    # 3. Call LLM
    try:
        client = get_llm_client(provider="groq")
        model = "meta-llama/llama-4-scout-17b-16e-instruct"

        response = await client.chat_completion(
            messages=[{"role": "user", "content": llm_messages}],
            model=model,
            temperature=0.5,
            max_tokens=700,
            stream=False,
        )

        answer = response.content.strip() if response.content else "(No answer generated)"

        return {
            "file_id": str(file_id),
            "prompt": prompt,
            "answer": answer,
        }

    except Exception as e:
        logger.error(f"File prompt failed: {str(e)}", exc_info=True)
        raise HTTPException(500, detail=f"Error generating answer: {str(e)}")
