from starlette.types import Message
from fastapi import HTTPException, Request, Response
from fastapi.responses import JSONResponse
from fastapi import status
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable
import json

from utils.logger import Logger


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        logger = Logger.setup_logger()

        logger.info(f"요청 URL: {request.method} {request.url.path}")
        logger.info(f"요청 헤더: {request.headers}")

        if request.method in ("POST", "PUT", "PATCH"):
            body = await request.body()
            logger.info(f"요청 본문: {body.decode('utf-8')}")

        try:
            # 응답 가로채기를 위한 send 래퍼
            response_body = []

            async def send_wrapper(message: Message) -> None:
                if message.get("type") == "http.response.body":
                    response_body.append(message.get("body", b""))

            # 다음 미들웨어/라우터 호출
            response = await call_next(request)

            # 응답 로그
            logger.info(f"응답 상태 코드: {response.status_code}")

            # 응답 본문 수집
            async for chunk in response.body_iterator:
                response_body.append(chunk)

            body = b"".join(response_body)

            # 로깅을 위해 응답 본문 기록
            if str(response.status_code).startswith("2"):
                try:
                    body_str = body.decode("utf-8")
                    logger.info(f"응답 본문: {body_str}")
                except Exception as e:
                    logger.error(f"에러 발생:{e}")

                # 원본 응답의 속성을 유지하면서 새 응답 생성
                return Response(
                    content=body,
                    status_code=response.status_code,
                    headers=dict(response.headers),
                    media_type=response.media_type or "application/json",
                )

            raise HTTPException(
                status_code=response.status_code,
                detail=json.loads(body.decode("utf-8"))["detail"],
            )

        except HTTPException as http_exception:
            error_response = {"detail": http_exception.detail}
            logger.error(f"HTTP 에러 발생: {http_exception.detail}", exc_info=True)
            return JSONResponse(
                content=error_response, status_code=http_exception.status_code
            )

        except Exception as e:
            error_response = {"detail": str(e)}  # TODO 내부 에러 발생으로 변경해야함
            logger.error(f"내부 에러 발생: {str(e)}", exc_info=True)
            return JSONResponse(content=error_response, status_code=500)
