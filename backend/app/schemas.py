from datetime import date, datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class CertificateTemplate(BaseModel):
    id: str
    name: str
    description: str
    html_template: str


class CertificatePayload(BaseModel):
    recipient_name: str = Field(min_length=1)
    course_name: str = Field(min_length=1)
    issue_date: date
    issuer_name: str | None = None
    issuer_signature_data_url: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class GenerateCertificateRequest(BaseModel):
    template_id: str
    payload: CertificatePayload


class BulkFailure(BaseModel):
    row_number: int
    reason: str


class CertificateRecord(BaseModel):
    certificate_id: str
    template_id: str
    payload: CertificatePayload
    verification_url: str
    qr_code_data_url: str
    public_certificate_path: str | None = None
    created_at: datetime


class BulkGenerationResponse(BaseModel):
    generated_count: int
    certificates: list[CertificateRecord]
    failed_rows: list[BulkFailure] = Field(default_factory=list)


class BulkCertificateDownloadRequest(BaseModel):
    certificate_ids: list[str] = Field(min_length=1)
    format: Literal['png', 'jpg'] = 'png'


class VerificationResponse(BaseModel):
    valid: bool
    message: str
    certificate: CertificateRecord | None = None
