from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from datetime import datetime
import uuid
import time
from app.utils.logger import get_logger


logger = get_logger("middleware")


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Middleware for centralized error handling."""
    
    async def dispatch(self, request: Request, call_next):
        # Add request ID if not exists
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        
        try:
            response = await call_next(request)
            return response
        except Exception as exc:
            logger.error(
                "Unhandled error in middleware",
                extra={"extra_data": {
                    "request_id": request_id,
                    "path": request.url.path,
                    "method": request.method,
                    "error": str(exc)
                }}
            )
            
            return JSONResponse(
                status_code=500,
                content={
                    "detail": "Internal server error",
                    "request_id": request_id,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging requests and responses."""
    
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        start_time = time.time()
        
        logger.info(
            "Request received",
            extra={"extra_data": {
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "client": request.client.host if request.client else None
            }}
        )
        
        response = await call_next(request)
        
        process_time = time.time() - start_time
        
        logger.info(
            "Request processed",
            extra={"extra_data": {
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "process_time_ms": int(process_time * 1000)
            }}
        )
        
        # Add custom headers
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = str(process_time)
        
        return response