import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = ROOT / 'backend' / 'data' / 'certificates.json'
OUTPUT_DIR = ROOT / 'frontend' / 'public' / 'issued'


def _render_metadata(metadata: dict) -> str:
    if not metadata:
        return '<p class="empty">No additional metadata.</p>'

    rows = []
    for key, value in metadata.items():
        rows.append(
            f'<tr><th>{html.escape(str(key))}</th><td>{html.escape(str(value))}</td></tr>'
        )

    return '<table>' + ''.join(rows) + '</table>'


def _render_certificate_page(certificate: dict) -> str:
    payload = certificate.get('payload', {})
    metadata = payload.get('metadata') or {}

    certificate_id = html.escape(str(certificate.get('certificate_id', '')))
    recipient_name = html.escape(str(payload.get('recipient_name', '')))
    course_name = html.escape(str(payload.get('course_name', '')))
    issue_date = html.escape(str(payload.get('issue_date', '')))
    issuer_name = html.escape(str(payload.get('issuer_name', 'Not provided')))
    verification_url = html.escape(str(certificate.get('verification_url', '#')))

    return f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Certificate {certificate_id}</title>
  <style>
    body {{ margin: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(145deg, #f6f0e8, #f1fbf5); color: #15231e; }}
    main {{ max-width: 820px; margin: 3rem auto; background: white; border-radius: 20px; padding: 2.5rem; box-shadow: 0 22px 45px rgba(0, 0, 0, 0.12); }}
    h1 {{ margin-top: 0; font-size: 2rem; }}
    .grid {{ display: grid; grid-template-columns: 180px 1fr; gap: 0.5rem 1rem; margin: 1.5rem 0 2rem; }}
    .label {{ font-weight: 700; color: #365246; }}
    table {{ width: 100%; border-collapse: collapse; margin-top: 1rem; }}
    th, td {{ text-align: left; padding: 0.6rem 0.75rem; border: 1px solid #d6e1db; }}
    th {{ width: 30%; background: #f1f9f3; }}
    .verify {{ display: inline-block; margin-top: 1.5rem; padding: 0.7rem 1rem; border-radius: 999px; background: #165d47; color: white; text-decoration: none; font-weight: 700; }}
    .empty {{ color: #5a6d63; font-style: italic; }}
  </style>
</head>
<body>
  <main>
    <h1>Certificate Record</h1>
    <p>This page is exported for GitHub Pages hosting.</p>

    <section class="grid">
      <div class="label">Certificate ID</div><div>{certificate_id}</div>
      <div class="label">Recipient</div><div>{recipient_name}</div>
      <div class="label">Course</div><div>{course_name}</div>
      <div class="label">Issue Date</div><div>{issue_date}</div>
      <div class="label">Issuer</div><div>{issuer_name}</div>
    </section>

    <h2>Metadata</h2>
    {_render_metadata(metadata)}

    <a class="verify" href="{verification_url}">Verify Certificate</a>
  </main>
</body>
</html>
'''


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if not DATA_PATH.exists():
        print(f'No certificate data found at: {DATA_PATH}')
        return

    certificates = json.loads(DATA_PATH.read_text(encoding='utf-8'))
    index_payload = []

    for certificate in certificates:
        certificate_id = certificate.get('certificate_id')
        if not certificate_id:
            continue

        html_page = _render_certificate_page(certificate)
        output_path = OUTPUT_DIR / f'{certificate_id}.html'
        output_path.write_text(html_page, encoding='utf-8')

        payload = certificate.get('payload', {})
        index_payload.append(
            {
                'certificate_id': certificate_id,
                'recipient_name': payload.get('recipient_name'),
                'course_name': payload.get('course_name'),
                'issue_date': payload.get('issue_date'),
                'path': f'/issued/{certificate_id}.html',
            }
        )

    (OUTPUT_DIR / 'index.json').write_text(json.dumps(index_payload, indent=2), encoding='utf-8')
    print(f'Exported {len(index_payload)} certificate page(s) to {OUTPUT_DIR}')


if __name__ == '__main__':
    main()
