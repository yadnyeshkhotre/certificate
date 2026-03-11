import os
from dataclasses import dataclass
from pathlib import Path


def _optional_env(name: str) -> str | None:
    value = os.getenv(name)
    if value is None:
        return None
    value = value.strip()
    return value or None


def _is_vercel_runtime() -> bool:
    return os.getenv('VERCEL') == '1' or bool(os.getenv('VERCEL_ENV'))


def _default_data_dir() -> Path:
    configured_dir = os.getenv('CERT_DATA_DIR')
    if configured_dir:
        return Path(configured_dir)

    # Vercel bundles source at /var/task (read-only), so writes must use /tmp.
    if _is_vercel_runtime():
        return Path('/tmp/certificate-data')

    return Path(__file__).resolve().parents[1] / 'data'


@dataclass(frozen=True)
class Settings:
    data_dir: Path = _default_data_dir()
    supabase_url: str | None = _optional_env('SUPABASE_URL')
    supabase_service_role_key: str | None = _optional_env('SUPABASE_SERVICE_ROLE_KEY')
    frontend_verify_base_url: str = os.getenv(
        'FRONTEND_VERIFY_BASE_URL',
        'http://localhost:3000/verify?certificateId=',
    )
    allow_origins: tuple[str, ...] = tuple(
        origin.strip()
        for origin in os.getenv('ALLOW_ORIGINS', 'http://localhost:3000').split(',')
        if origin.strip()
    )


settings = Settings()
