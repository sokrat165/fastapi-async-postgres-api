from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime, timezone

class QandABase(BaseModel):
    question: str = Field(..., min_length=1, max_length=500)
    answer: str = Field(..., min_length=1)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class QandACreate(QandABase):
    """Used when creating a Q&A entry (manual or from AI)"""
    user_id: int | None = Field(None, ge=1, description="Optional user ID")


class QandAUpdate(BaseModel):
    question: str | None = Field(None, min_length=1, max_length=500)
    answer: str | None = Field(None, min_length=1)
    user_id: int | None = Field(None, ge=1)


class AskAIRequest(BaseModel):
    """Request body for AI generation endpoint /qanda/ask"""
    question: str = Field(..., min_length=3, max_length=800, description="The question to ask the AI")
    model: str = Field("command-a-03-2025", description="Cohere model to use")
    temperature: float = Field(0.7, ge=0.0, le=2.0, description="Creativity level")
    max_tokens: int = Field(600, ge=50, le=4096, description="Max tokens to generate")
    save_to_db: bool = Field(
        True,
        description="If true, automatically save the generated Q&A to database"
    )


class QandAOut(QandABase):
    id: int = Field(...)
    user_id: int | None = None

    model_config = ConfigDict(from_attributes=True)