from fastapi import Header, HTTPException, status


def verified_user_id(x_user_id: str | None = Header(default=None)) -> str:
    if not x_user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="X-User-ID is required")
    return x_user_id

