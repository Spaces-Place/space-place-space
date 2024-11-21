from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from utils.aws_config import AWSConfig, get_aws_config
from utils.jwt_handler import verify_jwt_token

# 요청이 들어올 때, Authorization 헤더에 토큰을 추출
user_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/sign-in")
async def userAuthenticate(token: str = Depends(user_oauth2_scheme), aws_config: AWSConfig = Depends(get_aws_config)):
    if not token:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="액세스 토큰이 누락되었습니다.")
    
    # token = token.split(" ")[1] 
    payload = verify_jwt_token(token, aws_config)
    return {
        "user_id": payload["user_id"]
    }