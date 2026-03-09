# QR Certificate Generator - Yadnyesh Khotre

A full-stack certificate platform built with **Next.js** (frontend) and **FastAPI** (backend). It lets teams generate verifiable certificates, embed QR codes, process bulk Excel uploads, and publish certificate pages to GitHub Pages.

## Features

- Generate certificates from reusable templates
- Automatic QR code creation pointing to verification pages
- Upload issuer signature (PNG) to stamp certificates
- Download styled certificate files as PNG/JPG
- Bulk generation from Excel (`.xlsx`) uploads
- Bulk ZIP download containing all generated participant certificates
- Built-in verification API and web verification UI
- GitHub Pages export workflow for hosted certificate pages
- Clean web dashboard for operations

## Quick Start

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Backend: `http://localhost:8000`  
Frontend: `http://localhost:3000`

## Environment Files

- Copy `backend/.env.example` to `backend/.env`
- Copy `frontend/.env.local.example` to `frontend/.env.local`
- Default logo path for certificates: `backend/assets/orbit-linker-logo.png`
- Optional override: set `CERT_COMPANY_LOGO_PATH` in backend environment
- Optional override: set `CERT_DATA_DIR` for where backend JSON data is stored

## Vercel Backend Note

- Vercel serverless code runs from `/var/task` (read-only), so runtime writes must use `/tmp`.
- Backend now auto-uses `/tmp/certificate-data` on Vercel unless `CERT_DATA_DIR` is set.
- `/tmp` is ephemeral; use external storage (Postgres, KV, Blob, S3, etc.) for durable data.

## API Endpoints

- `GET /health`
- `GET /api/templates`
- `GET /api/certificates`
- `GET /api/certificates/{certificate_id}`
- `GET /api/certificates/{certificate_id}/download?format=png|jpg`
- `POST /api/certificates/generate`
- `POST /api/certificates/bulk`
- `POST /api/certificates/bulk/download`
- `GET /api/verify/{certificate_id}`

## Bulk Excel Headers

Required columns in `.xlsx`:

- `recipient_name`
- `course_name`
- `issue_date` (`YYYY-MM-DD` or Excel date)

Optional: `issuer_name` and any custom columns (stored under metadata).

Bulk form also allows:

- common `Issuer Name` (used for all rows where `issuer_name` is not provided in Excel)
- common `Issuer Signature (PNG)` applied to all generated bulk certificates

When you use bulk generation in the UI, it now automatically downloads a ZIP file with:

- one certificate image per participant
- `manifest.json` mapping participant and certificate details to each file name

## GitHub Pages Export

```bash
cd backend
python scripts/export_github_pages.py
cd ../frontend
npm run build
```

Deploy `frontend/out` to GitHub Pages.
