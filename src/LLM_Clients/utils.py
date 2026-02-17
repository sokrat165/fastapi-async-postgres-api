# # src/llm_clients/utils.py  (or put in files.py for now)
# from src.LLM_Clients.factory import get_llm_client
# from src.LLM_Clients.base import LLMMessage

# async def generate_file_description(
#     public_url: str,
#     mime_type: str,
#     user_description: str | None = None,
# ) -> str:
#     """
#     Use Grok vision to describe/summarize the uploaded file.
#     Works for images and PDFs (as image).
#     """
#     xai_client = get_llm_client(provider="xai")

#     # Choose a vision-capable model (adjust based on your preference/cost)
#     model = "grok-2-vision-1212"          # Reliable vision model
#     # Or try newer: "grok-4-1-fast" if it supports vision in your tests

#     text_part = (
#         "You are an expert at analyzing documents and images. "
#         "Describe the content clearly and concisely.\n\n"
#         "Rules:\n"
#         "- If image/photo: describe scene, objects, colors, text (OCR), people (if any), overall meaning.\n"
#         "- If document/PDF/invoice/receipt: extract key facts (title, dates, names, amounts, companies, totals), "
#         "then give a 3-5 sentence summary of purpose and main points.\n"
#         "- Be factual, structured, and include any visible numbers/tables exactly.\n"
#         "- If unclear/handwritten, note that.\n"
#     )

#     if user_description:
#         text_part += f"\nUser provided description/context: {user_description}\n"

#     messages: list[LLMMessage] = [
#         {
#             "role": "user",
#             "content": [
#                 {"type": "text", "text": text_part},
#                 {
#                     "type": "image_url",
#                     "image_url": {"url": public_url}   # Supabase public URL
#                 },
#             ],
#         }
#     ]

#     try:
#         response = await xai_client.chat_completion(
#             messages=messages,
#             model=model,
#             temperature=0.35,       # lower for factual extraction
#             max_tokens=600,
#             stream=False,
#         )
#         return response.content.strip() or "(No description generated)"
#     except Exception as e:
#         logger.error(f"Grok description failed: {str(e)}")
#         return f"AI description unavailable: {str(e)}"

# src/llm_clients/utils.py
import asyncio
import logging
from src.LLM_Clients.factory import get_llm_client
from src.LLM_Clients.base import LLMMessage

logger = logging.getLogger(__name__)

async def generate_file_description(
    public_url: str,
    mime_type: str,
    user_description: str | None = None,
    timeout: float = 30.0,
) -> str:
    """
    Use Grok vision to describe/summarize the uploaded file.
    Works for images and PDFs (as image).
    """

    # Get LLM client (implements LLMClient interface)
    xai_client = get_llm_client(provider="xai")
    model = "grok-2-vision-1212"  # Vision-capable Grok model

    # Instruction text
    text_part = (
        "You are an expert at analyzing documents and images. "
        "Describe the content clearly and concisely.\n\n"
        "Rules:\n"
        "- Images: describe objects, colors, text, people, overall meaning.\n"
        "- Documents/PDFs: extract key facts and give a 3-5 sentence summary.\n"
    )

    if user_description:
        text_part += f"\nUser description/context: {user_description}\n"

    # Build LLM messages
    messages: list[LLMMessage] = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": text_part},
                {"type": "image_url", "image_url": {"url": public_url}},
            ],
        }
    ]

    try:
        # Use Base LLMClient with timeout
        response = await asyncio.wait_for(
            xai_client.chat_completion(
                messages=messages,
                model=model,
                temperature=0.35,
                max_tokens=600,
                stream=False,
            ),
            timeout=timeout,
        )
        return response.content or "(No description generated)"

    except asyncio.TimeoutError:
        logger.warning(f"Grok client timed out for file {public_url}")
        return "(AI description timed out)"

    except Exception as e:
        logger.error(f"Grok description failed for {public_url}: {str(e)}")
        return "(AI description unavailable)"
