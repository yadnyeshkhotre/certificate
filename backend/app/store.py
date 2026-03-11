import json
from pathlib import Path
from threading import Lock
from typing import Any

from .config import settings
from .schemas import CertificateRecord, CertificateTemplate

try:
    from supabase import Client, create_client
except Exception:  # pragma: no cover - optional at runtime if JSON fallback is used.
    Client = Any  # type: ignore[assignment]
    create_client = None  # type: ignore[assignment]

_store_lock = Lock()
_templates_path = settings.data_dir / 'templates.json'
_certificates_path = settings.data_dir / 'certificates.json'
_supabase_client: Client | None = None


def _default_templates() -> list[dict[str, str]]:
    return [
        {
            'id': 'classic',
            'name': 'Classic Completion Certificate',
            'description': 'A clean, formal template for completion certificates.',
            'html_template': (
                '<h1>Certificate of Completion</h1>'
                '<p>This certifies {{recipient_name}} has completed {{course_name}} on {{issue_date}}.</p>'
            ),
        },
        {
            'id': 'modern',
            'name': 'Modern Achievement Certificate',
            'description': 'A modern style suitable for workshops and events.',
            'html_template': (
                '<h1>Achievement Certificate</h1>'
                '<p>{{recipient_name}} is recognized for {{course_name}} dated {{issue_date}}.</p>'
            ),
        },
    ]


def _use_supabase_storage() -> bool:
    if settings.supabase_url and settings.supabase_service_role_key:
        return True
    if settings.supabase_url or settings.supabase_service_role_key:
        raise RuntimeError('Both SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set.')
    return False


def _get_supabase_client() -> Client | None:
    if not _use_supabase_storage():
        return None

    if create_client is None:
        raise RuntimeError('Supabase client is unavailable. Install the "supabase" package.')

    global _supabase_client
    if _supabase_client is None:
        _supabase_client = create_client(settings.supabase_url, settings.supabase_service_role_key)
    return _supabase_client


def initialize() -> None:
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    if not _templates_path.exists():
        _write_json(_templates_path, _default_templates())
    if not _use_supabase_storage() and not _certificates_path.exists():
        _write_json(_certificates_path, [])


def _read_json(path: Path, fallback: object) -> object:
    if not path.exists():
        return fallback
    # Accept files with or without UTF-8 BOM.
    with path.open('r', encoding='utf-8-sig') as file:
        return json.load(file)


def _write_json(path: Path, payload: object) -> None:
    with path.open('w', encoding='utf-8') as file:
        json.dump(payload, file, indent=2)


def load_templates() -> list[CertificateTemplate]:
    initialize()
    data = _read_json(_templates_path, _default_templates())
    return [CertificateTemplate.model_validate(item) for item in data]


def get_template(template_id: str) -> CertificateTemplate | None:
    for template in load_templates():
        if template.id == template_id:
            return template
    return None


def _load_certificates_from_json() -> list[CertificateRecord]:
    data = _read_json(_certificates_path, [])
    return [CertificateRecord.model_validate(item) for item in data]


def _load_certificates_from_supabase(client: Client) -> list[CertificateRecord]:
    response = client.table('certificates').select('*').order('created_at', desc=False).execute()
    rows = response.data or []
    return [CertificateRecord.model_validate(item) for item in rows]


def load_certificates() -> list[CertificateRecord]:
    initialize()
    client = _get_supabase_client()
    if client is None:
        return _load_certificates_from_json()
    return _load_certificates_from_supabase(client)


def save_certificates(certificates: list[CertificateRecord]) -> None:
    initialize()
    serializable = [record.model_dump(mode='json') for record in certificates]
    client = _get_supabase_client()
    if client is not None:
        if serializable:
            client.table('certificates').upsert(serializable, on_conflict='certificate_id').execute()
        return

    with _store_lock:
        _write_json(_certificates_path, serializable)


def append_certificates(new_records: list[CertificateRecord]) -> None:
    if not new_records:
        return

    serializable = [record.model_dump(mode='json') for record in new_records]
    client = _get_supabase_client()
    if client is not None:
        client.table('certificates').upsert(serializable, on_conflict='certificate_id').execute()
        return

    existing = load_certificates()
    existing.extend(new_records)
    save_certificates(existing)


def get_certificate(certificate_id: str) -> CertificateRecord | None:
    initialize()
    client = _get_supabase_client()
    if client is not None:
        response = (
            client.table('certificates')
            .select('*')
            .eq('certificate_id', certificate_id)
            .limit(1)
            .execute()
        )
        rows = response.data or []
        if not rows:
            return None
        return CertificateRecord.model_validate(rows[0])

    for record in _load_certificates_from_json():
        if record.certificate_id == certificate_id:
            return record
    return None
