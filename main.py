from fastapi import FastAPI
from core.settings import settings
from core.endpoints import api


app: FastAPI = FastAPI(
    title=settings.PROJECT_NAME, version=settings.VERSION, docs_url=settings.DOCS_URL, redoc_url=None
)
app.include_router(api.router, prefix=settings.API_PREFIX)
