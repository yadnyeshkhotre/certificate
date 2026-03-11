import argparse
import json
import os
from pathlib import Path

from supabase import create_client


def _load_rows(source: Path) -> list[dict]:
    with source.open('r', encoding='utf-8-sig') as handle:
        payload = json.load(handle)
    if not isinstance(payload, list):
        raise ValueError('Source JSON must be an array of certificate objects.')
    return payload


def _build_parser() -> argparse.ArgumentParser:
    default_source = Path(__file__).resolve().parents[1] / 'data' / 'certificates.json'
    parser = argparse.ArgumentParser(description='Migrate certificate JSON rows to Supabase.')
    parser.add_argument(
        '--source',
        type=Path,
        default=default_source,
        help=f'Path to source JSON file (default: {default_source})',
    )
    parser.add_argument(
        '--batch-size',
        type=int,
        default=200,
        help='Rows per upsert batch (default: 200).',
    )
    return parser


def main() -> None:
    args = _build_parser().parse_args()

    if args.batch_size <= 0:
        raise SystemExit('Batch size must be greater than 0.')

    supabase_url = os.getenv('SUPABASE_URL', '').strip()
    supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY', '').strip()
    if not supabase_url or not supabase_key:
        raise SystemExit('Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY before running migration.')

    source = args.source
    if not source.exists():
        raise SystemExit(f'Source file not found: {source}')

    rows = _load_rows(source)
    if not rows:
        print('No rows found. Nothing to migrate.')
        return

    client = create_client(supabase_url, supabase_key)
    total = len(rows)
    migrated = 0

    for offset in range(0, total, args.batch_size):
        batch = rows[offset : offset + args.batch_size]
        client.table('certificates').upsert(batch, on_conflict='certificate_id').execute()
        migrated += len(batch)
        print(f'Upserted {migrated}/{total}')

    print(f'Done. Migrated {migrated} certificates to Supabase.')


if __name__ == '__main__':
    main()
