import logging
from typing import Any, Callable, Dict

from fastapi.routing import APIRoute
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger()


class LoggingAPIRoute(APIRoute):

    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            await self._request_log(request)
            response: Response = await original_route_handler(request)
            self._response_log(request, response)
            return response

        return custom_route_handler

    @staticmethod
    def _has_json_body(request: Request) -> bool:
        if (
            request.method in ("POST", "PUT", "PATCH") and 
            request.headers.get("content-type") == "application/json"
				):
            return True
        return False

    async def _request_log(self, request: Request) -> None:
        extra: Dict[str, Any] = {
            "httpMethod": request.method,
            "url": request.url.path,
            "headers": request.headers,
            "queryParams": request.query_params,
        }

        if self._has_json_body(request):
            request_body = await request.body()
            extra["body"] = request_body.decode("UTF-8")

        logger.info(f"요청 URL: {extra['httpMethod']} {extra['url']}", extra=extra)
        logger.info(f"쿼리 파라미터: {extra['queryParams']}", extra=extra)
        logger.info(f"요청 데이터: {extra.get('body', '')}", extra=extra)

    @staticmethod
    def _response_log(request: Request, response: Response) -> Dict[str, str]:
        extra: Dict[str, str] = {
            "httpMethod": request.method,
            "url": request.url.path,
            "body": response.body.decode("UTF-8")
        }
		
        logger.info(f"응답 데이터: {extra['body']}", extra=extra)