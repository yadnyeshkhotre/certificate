'use client';

import { FormEvent, useMemo, useState } from 'react';

import {
  buildCertificateDownloadUrl,
  CertificateRecord,
  CertificateTemplate,
  generateCertificate,
} from '@/lib/api';

type Props = {
  templates: CertificateTemplate[];
};

function parseMetadata(raw: string): Record<string, unknown> {
  const value = raw.trim();
  if (!value) {
    return {};
  }

  const parsed = JSON.parse(value);
  if (typeof parsed !== 'object' || parsed === null || Array.isArray(parsed)) {
    throw new Error('Metadata must be a JSON object.');
  }

  return parsed as Record<string, unknown>;
}

function readFileAsDataUrl(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => {
      if (typeof reader.result === 'string') {
        resolve(reader.result);
        return;
      }
      reject(new Error('Unable to read signature file.'));
    };
    reader.onerror = () => reject(new Error('Unable to read signature file.'));
    reader.readAsDataURL(file);
  });
}

export function CertificateForm({ templates }: Props) {
  const [templateId, setTemplateId] = useState<string>(templates[0]?.id ?? '');
  const [recipientName, setRecipientName] = useState('');
  const [courseName, setCourseName] = useState('');
  const [issueDate, setIssueDate] = useState('');
  const [issuerName, setIssuerName] = useState('');
  const [signatureFile, setSignatureFile] = useState<File | null>(null);
  const [metadataText, setMetadataText] = useState('{"batch": "2026"}');

  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<CertificateRecord | null>(null);

  const disabled = useMemo(() => {
    return busy || !templateId || !recipientName || !courseName || !issueDate;
  }, [busy, templateId, recipientName, courseName, issueDate]);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setError(null);
    setResult(null);

    try {
      const metadata = parseMetadata(metadataText);
      let issuerSignatureDataUrl: string | undefined;

      if (signatureFile) {
        if (signatureFile.type !== 'image/png') {
          throw new Error('Issuer signature must be a PNG image.');
        }
        if (signatureFile.size > 2 * 1024 * 1024) {
          throw new Error('Issuer signature PNG must be smaller than 2MB.');
        }
        issuerSignatureDataUrl = await readFileAsDataUrl(signatureFile);
      }

      const certificate = await generateCertificate({
        template_id: templateId,
        payload: {
          recipient_name: recipientName,
          course_name: courseName,
          issue_date: issueDate,
          issuer_name: issuerName || undefined,
          issuer_signature_data_url: issuerSignatureDataUrl,
          metadata,
        },
      });
      setResult(certificate);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Generation failed.';
      setError(message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="panel">
      <h2>Generate Single Certificate</h2>
      <form onSubmit={onSubmit}>
        <label>
          Template
          <select value={templateId} onChange={(event) => setTemplateId(event.target.value)}>
            {templates.map((template) => (
              <option key={template.id} value={template.id}>
                {template.name}
              </option>
            ))}
          </select>
        </label>

        <label>
          Recipient Name
          <input
            value={recipientName}
            onChange={(event) => setRecipientName(event.target.value)}
            placeholder="Aarav Sharma"
            required
          />
        </label>

        <label>
          Course Name
          <input
            value={courseName}
            onChange={(event) => setCourseName(event.target.value)}
            placeholder="Advanced Web Development"
            required
          />
        </label>

        <label>
          Issue Date
          <input type="date" value={issueDate} onChange={(event) => setIssueDate(event.target.value)} required />
        </label>

        <label>
          Issuer Name
          <input
            value={issuerName}
            onChange={(event) => setIssuerName(event.target.value)}
            placeholder="Training Coordinator"
          />
        </label>

        <label>
          Issuer Signature (PNG)
          <input
            type="file"
            accept="image/png"
            onChange={(event) => setSignatureFile(event.target.files?.[0] ?? null)}
          />
          <div className="small">
            Upload a transparent PNG signature to print on the certificate.
            {signatureFile ? ` Selected: ${signatureFile.name}` : ''}
          </div>
        </label>

        <label>
          Metadata (JSON object)
          <textarea value={metadataText} onChange={(event) => setMetadataText(event.target.value)} />
          <div className="small">Extra info like score, batch, or department.</div>
        </label>

        <button type="submit" disabled={disabled}>
          {busy ? 'Generating...' : 'Generate Certificate'}
        </button>
      </form>

      {error && <div className="result bad">{error}</div>}

      {result && (
        <div className="result good">
          <div>
            <strong>Certificate ID:</strong> <span className="mono">{result.certificate_id}</span>
          </div>
          <div>
            <strong>Verification URL:</strong>{' '}
            <a href={result.verification_url} target="_blank" rel="noreferrer">
              {result.verification_url}
            </a>
          </div>
          <div>
            <strong>Hosted Page Path:</strong> <span className="mono">{result.public_certificate_path}</span>
          </div>
          <div className="download-actions">
            <a
              className="download-link"
              href={buildCertificateDownloadUrl(result.certificate_id, 'png')}
              target="_blank"
              rel="noreferrer"
            >
              Download PNG Certificate
            </a>
            <a
              className="download-link"
              href={buildCertificateDownloadUrl(result.certificate_id, 'jpg')}
              target="_blank"
              rel="noreferrer"
            >
              Download JPG Certificate
            </a>
          </div>
          <img src={result.qr_code_data_url} className="qr" alt="Certificate QR code" />
        </div>
      )}
    </section>
  );
}
