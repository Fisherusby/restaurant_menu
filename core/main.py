from fastapi import FastAPI

from core.docs.project_description import description
from core.endpoints import api
from core.settings import settings

app: FastAPI = FastAPI(
    docs_url=settings.DOCS_URL,
    openapi_url=f'{settings.API_PREFIX}/openapi.json',
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    contact={'name': settings.CONTACT_NAME, 'email': settings.CONTACT_EMAIL},
    summary=settings.SUMMARY,
    description=description,
    redoc_url=None,
    openapi_tags=api.tags_metadata,
)
app.include_router(api.router, prefix=settings.API_PREFIX)
