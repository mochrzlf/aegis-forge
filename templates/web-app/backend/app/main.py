"""FastAPI application entrypoint."""
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.api import auth, health, users
from app.core.config import settings
from app.core.envelope import ErrorCode, err
from app.core.logging import configure_logging

configure_logging()

app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    docs_url="/docs" if not settings.is_production else None,
    redoc_url=None,
)


@app.exception_handler(RequestValidationError)
async def validation_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=err(ErrorCode.VALIDATION_ERROR, "Invalid request", {"errors": exc.errors()}),
    )


@app.exception_handler(Exception)
async def unhandled_handler(request: Request, exc: Exception):
    # No internals leaked (AGENTS.md §3.1).
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=err(ErrorCode.INTERNAL_ERROR, "Internal server error"),
    )


app.include_router(health.router, prefix=settings.API_PREFIX)
app.include_router(auth.router, prefix=settings.API_PREFIX)
app.include_router(users.router, prefix=settings.API_PREFIX)
