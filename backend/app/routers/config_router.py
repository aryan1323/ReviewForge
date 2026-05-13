from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user, get_db
from app.models.user import User
from app.models.user_config import UserConfig
from app.schemas.config import ConfigRequest, ConfigResponse

router = APIRouter(prefix="/config", tags=["config"])


def _to_response(config: UserConfig, user_id: str) -> ConfigResponse:
    return ConfigResponse(
        github_token=config.github_token,
        github_webhook_secret=config.github_webhook_secret,
        azure_openai_api_key=config.azure_openai_api_key,
        azure_openai_endpoint=config.azure_openai_endpoint,
        azure_deployment=config.azure_deployment,
        azure_api_version=config.azure_api_version,
        azure_embedding_deployment=config.azure_embedding_deployment,
        webhook_url=f"/webhook/github/{user_id}",
    )


@router.get("", response_model=ConfigResponse)
async def get_config(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(UserConfig).where(UserConfig.user_id == user.id))
    config = result.scalar_one_or_none()
    if not config:
        config = UserConfig(user_id=user.id)
        db.add(config)
        await db.commit()
        await db.refresh(config)
    return _to_response(config, str(user.id))


@router.put("", response_model=ConfigResponse)
async def update_config(
    body: ConfigRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(UserConfig).where(UserConfig.user_id == user.id))
    config = result.scalar_one_or_none()
    if not config:
        config = UserConfig(user_id=user.id)
        db.add(config)

    for field, value in body.model_dump().items():
        if value is not None:
            setattr(config, field, value)

    await db.commit()
    await db.refresh(config)
    return _to_response(config, str(user.id))
