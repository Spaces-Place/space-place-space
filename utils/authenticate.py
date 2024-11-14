from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from utils.jwt_handler import verify_jwt_token

# 요청이 들어올 때, Authorization 헤더에 토큰을 추출
user_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/sign-in")
async def userAuthenticate(token: str = Depends(user_oauth2_scheme)):
    if not token:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="액세스 토큰이 누락되었습니다.")
    
    payload = verify_jwt_token(token)
    return {
        "id": payload["id"],
        "user_id": payload["user_id"]
    }