from time import time
from fastapi import HTTPException, status
from jose import jwt

from services.aws_service import get_aws_service


# JWT 토큰 검증
def verify_jwt_token(token: str) -> dict:
    secret = get_aws_service().get_jwt_secret()

    try:
        payload = jwt.decode(token, secret, algorithms=["HS256"])
        if "exp" not in payload or time() > payload["exp"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="다시 로그인해주세요"
            )

        return payload

    except jwt.JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="다시 로그인해주세요."
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="잘못된 접근입니다. 로그인을 해주세요",
        )
