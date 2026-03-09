from fastapi import APIRouter

from ..schemas import VerificationResponse
from ..store import get_certificate

router = APIRouter(prefix='/verify', tags=['verification'])


@router.get('/{certificate_id}', response_model=VerificationResponse)
def verify_certificate(certificate_id: str) -> VerificationResponse:
    certificate = get_certificate(certificate_id)
    if certificate is None:
        return VerificationResponse(valid=False, message='Certificate not found.')
    return VerificationResponse(valid=True, message='Certificate is valid.', certificate=certificate)
