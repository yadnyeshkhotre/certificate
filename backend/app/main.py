from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .routers import certificates, templates, verification
from .store import initialize

initialize()

app = FastAPI(
    title='QR Certificate Generator API',
    version='1.0.0',
    description='Generate, manage, and verify certificates with QR codes.',
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.allow_origins),
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.get('/health')
def health_check() -> dict[str, str]:
    return {'status': 'ok'}


app.include_router(templates.router, prefix='/api')
app.include_router(certificates.router, prefix='/api')
app.include_router(verification.router, prefix='/api')
