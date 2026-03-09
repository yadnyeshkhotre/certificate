import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    data_dir: Path = Path(os.getenv('CERT_DATA_DIR', Path(__file__).resolve().parents[1] / 'data'))
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
