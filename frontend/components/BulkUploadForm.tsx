'use client';

import { FormEvent, useMemo, useState } from 'react';

import {
  BulkGenerationResponse,
  CertificateTemplate,
  bulkGenerate,
  downloadBulkCertificatesZip,
} from '@/lib/api';

type Props = {
  templates: CertificateTemplate[];
};

export function BulkUploadForm({ templates }: Props) {
  const [templateId, setTemplateId] = useState<string>(templates[0]?.id ?? '');
  const [file, setFile] = useState<File | null>(null);
  const [issuerName, setIssuerName] = useState('');
  const [signatureFile, setSignatureFile] = useState<File | null>(null);

  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<BulkGenerationResponse | null>(null);
  const [downloadMessage, setDownloadMessage] = useState<string | null>(null);

  const disabled = useMemo(() => busy || !templateId || !file, [busy, templateId, file]);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!file) {
      return;
    }

    setBusy(true);
    setError(null);
    setResult(null);
    setDownloadMessage(null);

    try {
      if (signatureFile) {
        if (signatureFile.type !== 'image/png') {
          throw new Error('Issuer signature must be a PNG image.');
        }
        if (signatureFile.size > 2 * 1024 * 1024) {
          throw new Error('Issuer signature PNG must be smaller than 2MB.');
        }
      }

      const response = await bulkGenerate({
        template_id: templateId,
        file,
        issuer_name: issuerName || undefined,
        issuer_signature_file: signatureFile || undefined,
      });
      setResult(response);

      if (response.generated_count > 0) {
        try {
          const certificateIds = response.certificates.map((certificate) => certificate.certificate_id);
          const zipResponse = await downloadBulkCertificatesZip({
            certificate_ids: certificateIds,
            format: 'png',
          });

          const link = document.createElement('a');
          const downloadUrl = URL.createObjectURL(zipResponse.blob);
          link.href = downloadUrl;
          link.download = zipResponse.filename;
          document.body.appendChild(link);
          link.click();
          link.remove();
          URL.revokeObjectURL(downloadUrl);

          setDownloadMessage(`ZIP downloaded with ${zipResponse.generated_count} certificate(s).`);
        } catch (zipErr) {
          const zipMessage =
            zipErr instanceof Error ? zipErr.message : 'ZIP download failed after generation.';
          setError(`Certificates generated, but ZIP download failed: ${zipMessage}`);
        }
      } else {
        setDownloadMessage('No certificates were generated, so no ZIP was downloaded.');
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Bulk generation failed.';
      setError(message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="panel">
      <h2>Bulk Generate from Excel</h2>
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
          Excel File (`.xlsx`)
          <input type="file" accept=".xlsx" onChange={(event) => setFile(event.target.files?.[0] ?? null)} />
        </label>

        <label>
          Issuer Name (applies to all rows unless Excel has `issuer_name`)
          <input
            value={issuerName}
            onChange={(event) => setIssuerName(event.target.value)}
            placeholder="Training Coordinator"
          />
        </label>

        <label>
          Issuer Signature (PNG, applies to all rows)
          <input
            type="file"
            accept="image/png"
            onChange={(event) => setSignatureFile(event.target.files?.[0] ?? null)}
          />
          <div className="small">
            {signatureFile
              ? `Selected: ${signatureFile.name}`
              : 'Upload one PNG signature to stamp all bulk certificates.'}
          </div>
        </label>

        <button type="submit" disabled={disabled}>
          {busy ? 'Uploading...' : 'Generate in Bulk'}
        </button>
      </form>

      <p className="small">
        Required headers: <span className="mono">recipient_name, course_name, issue_date</span>
      </p>

      {error && <div className="result bad">{error}</div>}

      {result && (
        <div className="result good">
          <div><strong>Generated:</strong> {result.generated_count}</div>
          <div><strong>Failed rows:</strong> {result.failed_rows.length}</div>
          {downloadMessage && <div className="small">{downloadMessage}</div>}
          {result.failed_rows.length > 0 && (
            <div className="small">
              {result.failed_rows.map((failure) => (
                <div key={`${failure.row_number}-${failure.reason}`}>
                  Row {failure.row_number}: {failure.reason}
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </section>
  );
}
