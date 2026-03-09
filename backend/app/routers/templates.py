from fastapi import APIRouter

from ..schemas import CertificateTemplate
from ..store import load_templates

router = APIRouter(prefix='/templates', tags=['templates'])


@router.get('', response_model=list[CertificateTemplate])
def list_templates() -> list[CertificateTemplate]:
    return load_templates()
