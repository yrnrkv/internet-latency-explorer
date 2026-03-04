from fastapi import HTTPException, status

from app.config import settings


def verify_api_key(key: str) -> None:
    if key not in settings.api_keys:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )
