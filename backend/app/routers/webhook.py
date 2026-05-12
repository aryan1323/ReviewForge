from fastapi import APIRouter, Depends, Header, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db
from app.services.webhook_service import WebhookService

router = APIRouter(prefix="/webhook", tags=["webhook"])


@router.post("/github", status_code=202)
async def github_webhook(
    request: Request,
    x_hub_signature_256: str = Header(...),
    x_github_event: str = Header(...),
    db: AsyncSession = Depends(get_db),
) -> dict:
    body = await request.body()
    await WebhookService().handle(
        event=x_github_event,
        signature=x_hub_signature_256,
        body=body,
        db=db,
    )
    return {"status": "accepted"}
