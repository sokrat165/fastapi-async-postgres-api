# src/routers/qanda-ai.py
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from src.LLM_Client.cohere_client import get_co_client
from src.core.security import get_current_user
from src.core.database import get_chosen_db
from src.schemas.qanda import AskAIRequest, QandACreate
from src.crud.qanda import QandARepository

router = APIRouter(
    prefix="/qanda",
    tags=["qanda-ai"],
    responses={500: {"description": "LLM service error"}},
)


@router.post(
    "/ask",
    response_model=dict,
    summary="Ask AI → generate answer → auto-save to DB (default: yes)",
)
async def ask_ai_and_save(
    req: AskAIRequest,
    current_user=Depends(get_current_user),
    db=Depends(get_chosen_db),
    co_client=Depends(get_co_client),
):
    try:
        response = await co_client.chat(
            model=req.model,
            messages=[{"role": "user", "content": req.question}],
            temperature=req.temperature,
            max_tokens=req.max_tokens,
        )

        answer_text = response.message.content[0].text.strip()

        result = {
            "question": req.question,
            "answer": answer_text,
            "model": req.model,
            "temperature": req.temperature,
            "max_tokens_requested": req.max_tokens,
        }

        if req.save_to_db:
            repo = QandARepository(db)
            new_qanda = QandACreate(
                question=req.question,
                answer=answer_text,
                user_id=current_user.id,
            )
            saved = await repo.create(new_qanda)

            result.update({
                "saved": True,
                "qanda_id": saved.id,
                "created_at": (
                    saved.timestamp.isoformat()
                    if hasattr(saved, "timestamp") else None
                )
            })

        return result

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate or save answer: {str(exc)}"
        ) from exc


@router.post(
    "/ask-stream",
    summary="Ask AI – streaming response (no auto-save)",
)
async def ask_ai_stream(
    req: AskAIRequest,
    co_client=Depends(get_co_client),
):
    async def event_generator():
        try:
            # Important: NO await here when using AsyncClientV2
            stream = co_client.chat_stream(
                model=req.model,
                messages=[{"role": "assistant", "content": req.question}],
                temperature=req.temperature,
                max_tokens=req.max_tokens,
            )

            async for chunk in stream:
                if chunk.type == "content-delta":
                    text = chunk.delta.message.content.text
                    if text:  # avoid yielding empty chunks
                        yield text

        except Exception as e:
            yield f"\n[ERROR] {str(e)}"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache"},
    )