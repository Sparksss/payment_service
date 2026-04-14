from fastapi import FastAPI
from app.api.v1.payments import router as payment_router
from app.core.config import settings


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description="B2B сервис для управления платежами (Cash/Acquiring)",
        version=settings.VERSION,
        docs_url="/api/docs",
        openapi_url="/api/openapi.json"
    )

    app.include_router(payment_router, prefix="/api/v1")

    @app.get("/health")
    async def health_check():
        return {
            "status": "ok",
            "project": settings.PROJECT_NAME,
            "version": settings.VERSION
        }

    return app

app = create_app()