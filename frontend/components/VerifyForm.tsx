'use client';

import { FormEvent, useEffect, useState } from 'react';

import {
  buildCertificateDownloadUrl,
  VerificationResponse,
  verifyCertificate,
} from '@/lib/api';

type Props = {
  defaultCertificateId?: string;
  autoCheck?: boolean;
};

export function VerifyForm({ defaultCertificateId = '', autoCheck = false }: Props) {
  const [certificateId, setCertificateId] = useState(defaultCertificateId);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<VerificationResponse | null>(null);

  async function runVerification(targetId: string) {
    if (!targetId.trim()) {
      setError('Enter a certificate ID.');
      return;
    }

    setBusy(true);
    setError(null);

    try {
      const response = await verifyCertificate(targetId.trim());
      setResult(response);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Verification failed.';
      setError(message);
    } finally {
      setBusy(false);
    }
  }

  useEffect(() => {
    if (autoCheck && defaultCertificateId) {
      void runVerification(defaultCertificateId);
    }
  }, [autoCheck, defaultCertificateId]);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    await runVerification(certificateId);
  }

  return (
    <section className="panel">
      <h2>Verify Certificate</h2>
      <form onSubmit={onSubmit}>
        <label>
          Certificate ID
          <input
            value={certificateId}
            onChange={(event) => setCertificateId(event.target.value)}
            placeholder="Paste certificate ID"
          />
        </label>

        <button type="submit" disabled={busy}>{busy ? 'Checking...' : 'Verify'}</button>
      </form>

      {error && <div className="result bad">{error}</div>}

      {result && (
        <div className={`result ${result.valid ? 'good' : 'bad'}`}>
          <div><strong>Status:</strong> {result.valid ? 'Valid' : 'Invalid'}</div>
          <div>{result.message}</div>
          {result.certificate && (
            <>
              <div><strong>Recipient:</strong> {result.certificate.payload.recipient_name}</div>
              <div><strong>Course:</strong> {result.certificate.payload.course_name}</div>
              <div><strong>Issue Date:</strong> {result.certificate.payload.issue_date}</div>
              <div className="download-actions">
                <a
                  className="download-link"
                  href={buildCertificateDownloadUrl(result.certificate.certificate_id, 'png')}
                  target="_blank"
                  rel="noreferrer"
                >
                  Download PNG Certificate
                </a>
                <a
                  className="download-link"
                  href={buildCertificateDownloadUrl(result.certificate.certificate_id, 'jpg')}
                  target="_blank"
                  rel="noreferrer"
                >
                  Download JPG Certificate
                </a>
              </div>
            </>
          )}
        </div>
      )}
    </section>
  );
}
