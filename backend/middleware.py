from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from config.logger import set_request_id

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        set_request_id()
        response = await call_next(request)
        return response
