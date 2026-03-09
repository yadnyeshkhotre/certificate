import json
from pathlib import Path
from threading import Lock

from .config import settings
from .schemas import CertificateRecord, CertificateTemplate

_store_lock = Lock()
_templates_path = settings.data_dir / 'templates.json'
_certificates_path = settings.data_dir / 'certificates.json'


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


def initialize() -> None:
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    if not _templates_path.exists():
        _write_json(_templates_path, _default_templates())
    if not _certificates_path.exists():
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


def load_certificates() -> list[CertificateRecord]:
    initialize()
    data = _read_json(_certificates_path, [])
    return [CertificateRecord.model_validate(item) for item in data]


def save_certificates(certificates: list[CertificateRecord]) -> None:
    initialize()
    serializable = [record.model_dump(mode='json') for record in certificates]
    with _store_lock:
        _write_json(_certificates_path, serializable)


def append_certificates(new_records: list[CertificateRecord]) -> None:
    existing = load_certificates()
    existing.extend(new_records)
    save_certificates(existing)


def get_certificate(certificate_id: str) -> CertificateRecord | None:
    for record in load_certificates():
        if record.certificate_id == certificate_id:
            return record
    return None
