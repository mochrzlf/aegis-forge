from fastapi import FastAPI
from app.api.routes import router
from app.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="Algorithmic Trading & EA Risk Guardian Bridge API",
)

app.include_router(router)


@app.get("/healthz", tags=["Health"])
def health_check():
    return {"status": "ok", "app": settings.APP_NAME}
