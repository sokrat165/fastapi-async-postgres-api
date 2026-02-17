# # src/api/files.py
# from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
# from uuid import uuid4
# from src.api.dependencies.supabase_dependencies import get_supabase_context

# router = APIRouter(prefix="/files", tags=["files"])

# @router.post("/upload")
# async def upload_file(
#     file: UploadFile = File(...),
#     description: str = Form(...),
#     ctx = Depends(get_supabase_context)
# ):
#     user = ctx["user"]
#     supabase = ctx["supabase"]
#     db = ctx["db"]

#     try:
#         # Unique file name
#         ext = file.filename.split(".")[-1].lower()
#         filename = f"{uuid4()}.{ext}"
#         path = f"users/{user.id}/{filename}"

#         # Upload to Supabase Storage – change bucket name here
#         content = await file.read()
#         upload_res = supabase.storage.from_("user-documents").upload(   # ← changed
#             path=path,
#             file=content,
#             file_options={"content-type": file.content_type}
#         )

#         if not upload_res:
#             raise HTTPException(500, "Failed to upload file")

#         # Get public URL
#         public_url = supabase.storage.from_("user-documents").get_public_url(path)  # ← changed

#         # Save metadata to DB (add table/columns if not already)
#         stmt = insert(UserFile).values(
#             user_id=user.id,
#             description=description,
#             file_path=path,
#             public_url=public_url,
#             mime_type=file.content_type,
#             file_size=len(content)
#         )
#         await db.execute(stmt)
#         await db.commit()

#         return {
#             "message": "File uploaded successfully",
#             "url": public_url,
#             "description": description
#         }

#     except Exception as e:
#         raise HTTPException(500, f"Upload error: {str(e)}")



# ------------------------------------------------------------------------------------------------------------------







# # src/api/files.py

# from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
# from uuid import uuid4
# from src.api.dependencies.supabase_dependencies import get_supabase_context
# import logging
# from sqlalchemy import insert
# from src.models.user_files import UserFile

# from src.LLM_Clients.factory import get_llm_client
# from src.LLM_Clients.base import LLMMessage

# logger = logging.getLogger(__name__)

# router = APIRouter(prefix="/files", tags=["files"])

# # Configurable – change if you create a different bucket name
# BUCKET_NAME = "document"

# # Max file size for vision (Groq ~20MB per image)
# MAX_VISION_SIZE_BYTES = 20 * 1024 * 1024  # 20 MB

# async def get_standard_description(public_url: str, mime_type: str, file_size: int) -> str:
#     if file_size > MAX_VISION_SIZE_BYTES:
#         return "(File too large for vision analysis – description skipped)"

#     try:
#         client = get_llm_client(provider="groq")
#         model = "meta-llama/llama-4-scout-17b-16e-instruct" # Updated to current supported vision model

#         prompt = (
#             "Analyze this image/document and provide a structured summary:\n"
#             "- Content type (photo, invoice, receipt, contract, report, ID, screenshot, etc.)\n"
#             "- Main topic/purpose in one sentence\n"
#             "- Key visible details (dates, names, amounts, totals, titles – quote exactly)\n"
#             "- Short overall description (3–6 sentences)\n"
#             "Use bullet points. Be factual and accurate."
#         )

#         messages = [
#             {
#                 "role": "user",
#                 "content": [
#                     {"type": "text", "text": prompt},
#                     {"type": "image_url", "image_url": {"url": public_url}},
#                 ]
#             }
#         ]

#         response = await client.chat_completion(
#             messages=messages,
#             model=model,
#             temperature=0.4,
#             max_tokens=600,
#             stream=False,
#         )

#         return response.content.strip() or "(No description generated)"

#     except Exception as e:
#         logger.error(f"Standard description failed: {str(e)}")
#         return f"Description generation failed: {str(e)}"


# async def get_custom_llm_response(public_url: str, mime_type: str, file_size: int, user_prompt: str) -> str:
#     if file_size > MAX_VISION_SIZE_BYTES:
#         return "(File too large for vision analysis – custom response skipped)"

#     try:
#         client = get_llm_client(provider="groq")
#         model = "meta-llama/llama-4-scout-17b-16e-instruct"

#         full_prompt = (
#             f"{user_prompt.strip()}\n\n"
#             "Answer based **only** on the visible content in the image/document. "
#             "Be precise, quote exact text/numbers, and avoid guessing."
#         )

#         messages = [
#             {"role": "user", "content": [
#                 {"type": "text", "text": full_prompt},
#                 {"type": "image_url", "image_url": {"url": public_url}},
#             ]}
#         ]

#         response = await client.chat_completion(
#             messages=messages,
#             model=model,
#             temperature=0.5,
#             max_tokens=700,
#             stream=False,
#         )

#         return response.content.strip() or "(No answer generated)"

#     except Exception as e:
#         logger.error(f"Custom LLM response failed: {str(e)}")
#         return f"Custom prompt failed: {str(e)}"


# @router.post("/upload")
# async def upload_file(
#     file: UploadFile = File(...),
#     description: str = Form(...),           # required – your original field
#     prompt: str = Form(None),               # optional – question to LLM
#     ctx = Depends(get_supabase_context)
# ):
#     user = ctx["user"]
#     supabase = ctx["supabase"]
#     db = ctx["db"]

#     logger.info(f"Upload started by user {user.id}: {file.filename} ({file.content_type})")

#     try:
#         ext = file.filename.split(".")[-1].lower()
#         filename = f"{uuid4()}.{ext}"
#         path = f"users/{user.id}/{filename}"

#         content = await file.read()
#         file_size = len(content)

#         logger.info(f"File size: {file_size} bytes")

#         # Upload
#         upload_res = supabase.storage.from_(BUCKET_NAME).upload(
#             path=path,
#             file=content,
#             file_options={"content-type": file.content_type}
#         )

#         if not upload_res:
#             raise HTTPException(500, "Supabase upload returned empty response")

#         public_url = supabase.storage.from_(BUCKET_NAME).get_public_url(path)
#         logger.info(f"Public URL: {public_url}")

#         # Save to DB
#         stmt = insert(UserFile).values(
#             user_id=user.id,
#             description=description,
#             file_path=path,
#             public_url=public_url,
#             mime_type=file.content_type,
#             file_size=file_size
#         )
#         await db.execute(stmt)
#         await db.commit()
#         logger.info("Metadata saved to DB")

#         # Vision analysis
#         standard_desc = await get_standard_description(public_url, file.content_type, file_size)

#         custom_resp = None
#         if prompt and prompt.strip():
#             custom_resp = await get_custom_llm_response(public_url, file.content_type, file_size, prompt)

#         return {
#             "message": "File uploaded successfully",
#             "url": public_url,
#             "description": description,
#             "standard_description": standard_desc,
#             "custom_prompt": prompt if prompt else None,
#             "custom_response": custom_resp,
#         }

#     except Exception as e:
#         logger.error(f"Upload failed: {str(e)}", exc_info=True)
#         raise HTTPException(500, f"Upload error: {str(e)}")



# -------------------------------------------------------
# src/api/files.py# src/api/files.py

from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from uuid import uuid4
from src.api.dependencies.supabase_dependencies import get_supabase_context
import logging
from sqlalchemy import insert
from src.models.user_files import UserFile
from src.LLM_Clients.factory import get_llm_client
import io

# PDF & OCR imports
from PyPDF2 import PdfReader
from pdf2image import convert_from_bytes
import pytesseract

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/files", tags=["files"])

BUCKET_NAME = "document"
MAX_VISION_SIZE_BYTES = 20 * 1024 * 1024  # 20 MB

async def extract_pdf_text(content: bytes) -> str:
    """Extract text from PDF, fallback to OCR if needed"""
    try:
        reader = PdfReader(io.BytesIO(content))
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
        if text.strip():
            return text.strip()

        # OCR fallback for scanned PDFs
        pages = convert_from_bytes(content)
        ocr_text = "\n".join(pytesseract.image_to_string(page) for page in pages)
        return ocr_text.strip() or "(No text found in PDF via OCR)"
    except Exception as e:
        logger.error(f"PDF extraction failed: {str(e)}")
        return f"(PDF extraction failed: {str(e)})"

async def get_standard_description(public_url: str, mime_type: str, file_size: int, pdf_text: str = None) -> str:
    if file_size > MAX_VISION_SIZE_BYTES:
        return "(File too large for vision analysis – skipped)"
    
    try:
        client = get_llm_client(provider="groq")
        model = "meta-llama/llama-4-scout-17b-16e-instruct"
        
        if mime_type == "application/pdf" and pdf_text:
            content_text = pdf_text
            prompt = (
                "Analyze this PDF content and provide a structured summary:\n"
                "- Main topic/purpose in one sentence\n"
                "- Key details (dates, names, amounts, totals, titles – quote exactly)\n"
                "- Short overall description (3–6 sentences)\n"
                "Use bullet points. Be factual and accurate."
            )
            messages = [{"role": "user", "content": [{"type": "text", "text": f"{prompt}\n\n{content_text}"}]}]
        else:
            # image/document analysis via URL
            prompt = (
                "Analyze this image/document and provide a structured summary:\n"
                "- Content type (photo, invoice, receipt, contract, report, ID, screenshot, etc.)\n"
                "- Main topic/purpose in one sentence\n"
                "- Key visible details (dates, names, amounts, totals, titles – quote exactly)\n"
                "- Short overall description (3–6 sentences)\n"
                "Use bullet points. Be factual and accurate."
            )
            messages = [{"role": "user", "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": public_url}},
            ]}]
        
        response = await client.chat_completion(
            messages=messages,
            model=model,
            temperature=0.4,
            max_tokens=600,
            stream=False
        )
        return response.content.strip() or "(No description generated)"
    
    except Exception as e:
        logger.error(f"Standard description failed: {str(e)}")
        return f"Description generation failed: {str(e)}"

async def get_custom_llm_response(public_url: str, mime_type: str, file_size: int, user_prompt: str, pdf_text: str = None) -> str:
    if file_size > MAX_VISION_SIZE_BYTES:
        return "(File too large for vision analysis – custom response skipped)"
    
    try:
        client = get_llm_client(provider="groq")
        model = "meta-llama/llama-4-scout-17b-16e-instruct"

        full_prompt = f"{user_prompt.strip()}\n\nAnswer based **only** on the visible content. Be precise, quote exact text/numbers, and avoid guessing."
        
        if mime_type == "application/pdf" and pdf_text:
            messages = [{"role": "user", "content": [{"type": "text", "text": f"{full_prompt}\n\n{pdf_text}"}]}]
        else:
            messages = [{"role": "user", "content": [
                {"type": "text", "text": full_prompt},
                {"type": "image_url", "image_url": {"url": public_url}},
            ]}]
        
        response = await client.chat_completion(
            messages=messages,
            model=model,
            temperature=0.5,
            max_tokens=700,
            stream=False
        )
        return response.content.strip() or "(No answer generated)"
    
    except Exception as e:
        logger.error(f"Custom LLM response failed: {str(e)}")
        return f"Custom prompt failed: {str(e)}"

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    description: str = Form(...),
    prompt: str = Form(None),
    ctx = Depends(get_supabase_context)
):
    user = ctx["user"]
    supabase = ctx["supabase"]
    db = ctx["db"]

    logger.info(f"Upload started by user {user.id}: {file.filename} ({file.content_type})")
    
    try:
        ext = file.filename.split(".")[-1].lower()
        filename = f"{uuid4()}.{ext}"
        path = f"users/{user.id}/{filename}"

        content = await file.read()
        file_size = len(content)
        logger.info(f"File size: {file_size} bytes")

        # Upload to Supabase
        upload_res = supabase.storage.from_(BUCKET_NAME).upload(
            path=path,
            file=content,
            file_options={"content-type": file.content_type}
        )
        if not upload_res:
            raise HTTPException(500, "Supabase upload returned empty response")
        public_url = supabase.storage.from_(BUCKET_NAME).get_public_url(path)
        logger.info(f"Public URL: {public_url}")

        # Save to DB
        stmt = insert(UserFile).values(
            user_id=user.id,
            description=description,
            file_path=path,
            public_url=public_url,
            mime_type=file.content_type,
            file_size=file_size
        )
        await db.execute(stmt)
        await db.commit()
        logger.info("Metadata saved to DB")

        # Extract PDF text if PDF
        pdf_text = None
        if file.content_type == "application/pdf":
            pdf_text = await extract_pdf_text(content)

        # Generate standard and custom descriptions
        standard_desc = await get_standard_description(public_url, file.content_type, file_size, pdf_text)
        custom_resp = None
        if prompt and prompt.strip():
            custom_resp = await get_custom_llm_response(public_url, file.content_type, file_size, prompt, pdf_text)

        return {
            "message": "File uploaded successfully",
            "url": public_url,
            "description": description,
            "standard_description": standard_desc,
            "custom_prompt": prompt if prompt else None,
            "custom_response": custom_resp,
        }

    except Exception as e:
        logger.error(f"Upload failed: {str(e)}", exc_info=True)
        raise HTTPException(500, f"Upload error: {str(e)}")
