from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from src.database_client.supabase_client import get_supabase_db

router = APIRouter(prefix="/db-test", tags=["database-test"])

@router.get("/supabase-connection")
async def test_supabase_connection(db: AsyncSession = Depends(get_supabase_db)):
    try:
        result = await db.execute(text("SELECT 1"))
        value = result.scalar()
        return {
            "status": "success",
            "message": "Connected to Supabase",
            "test_result": value
        }
    except Exception as exc:
        # Print full traceback to your server console/logs
        import traceback
        traceback.print_exc()
        
        return {
            "status": "error",
            "detail": str(exc),
            "type": type(exc).__name__,
            "hint": "Check server console for full traceback"
        }