from datetime import datetime
from urllib.parse import quote
from uuid import uuid4

from ..config import settings
from ..schemas import CertificatePayload, CertificateRecord
from .qr_service import generate_qr_data_url


def _build_verification_url(certificate_id: str) -> str:
    base_url = settings.frontend_verify_base_url.strip()
    safe_id = quote(certificate_id)

    if '{id}' in base_url:
        return base_url.replace('{id}', safe_id)
    if base_url.endswith('=') or base_url.endswith('/'):
        return f'{base_url}{safe_id}'

    separator = '&' if '?' in base_url else '?'
    return f'{base_url}{separator}certificateId={safe_id}'


def create_certificate_record(template_id: str, payload: CertificatePayload) -> CertificateRecord:
    certificate_id = uuid4().hex
    verification_url = _build_verification_url(certificate_id)
    qr_code_data_url = generate_qr_data_url(verification_url)

    return CertificateRecord(
        certificate_id=certificate_id,
        template_id=template_id,
        payload=payload,
        verification_url=verification_url,
        qr_code_data_url=qr_code_data_url,
        public_certificate_path=f'/issued/{certificate_id}.html',
        created_at=datetime.utcnow(),
    )
