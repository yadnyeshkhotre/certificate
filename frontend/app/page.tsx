'use client';

import { useEffect, useState } from 'react';

import { BulkUploadForm } from '@/components/BulkUploadForm';
import { CertificateForm } from '@/components/CertificateForm';
import { VerifyForm } from '@/components/VerifyForm';
import { CertificateTemplate, fetchTemplates } from '@/lib/api';

export default function HomePage() {
  const [templates, setTemplates] = useState<CertificateTemplate[]>([]);
  const [loadingTemplates, setLoadingTemplates] = useState(true);
  const [templateError, setTemplateError] = useState<string | null>(null);

  useEffect(() => {
    async function loadTemplates() {
      setLoadingTemplates(true);
      setTemplateError(null);
      try {
        const list = await fetchTemplates();
        setTemplates(list);
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Unable to fetch templates.';
        setTemplateError(message);
      } finally {
        setLoadingTemplates(false);
      }
    }

    void loadTemplates();
  }, []);

  return (
    <main>
      <section className="hero">
        <h1>QR Certificate Generator</h1>
        <p>
          Generate secure certificates, embed QR verification links, process bulk Excel uploads,
          and export hosted certificate pages for GitHub Pages.
        </p>
      </section>

      {loadingTemplates && <p className="small">Loading templates...</p>}
      {templateError && <div className="result bad">{templateError}</div>}

      {!loadingTemplates && !templateError && templates.length === 0 && (
        <div className="result bad">
          No templates found. Add templates in <span className="mono">backend/data/templates.json</span>.
        </div>
      )}

      {!loadingTemplates && templates.length > 0 && (
        <section className="grid">
          <CertificateForm templates={templates} />
          <BulkUploadForm templates={templates} />
          <VerifyForm />
        </section>
      )}
    </main>
  );
}
