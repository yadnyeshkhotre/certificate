export type CertificateTemplate = {
  id: string;
  name: string;
  description: string;
  html_template: string;
};

export type CertificatePayload = {
  recipient_name: string;
  course_name: string;
  issue_date: string;
  issuer_name?: string;
  issuer_signature_data_url?: string;
  metadata?: Record<string, unknown>;
};

export type CertificateRecord = {
  certificate_id: string;
  template_id: string;
  payload: CertificatePayload;
  verification_url: string;
  qr_code_data_url: string;
  public_certificate_path?: string | null;
  created_at: string;
};

export type VerificationResponse = {
  valid: boolean;
  message: string;
  certificate?: CertificateRecord | null;
};

export type BulkFailure = {
  row_number: number;
  reason: string;
};

export type BulkGenerationResponse = {
  generated_count: number;
  certificates: CertificateRecord[];
  failed_rows: BulkFailure[];
};

export type BulkZipDownloadResponse = {
  blob: Blob;
  filename: string;
  generated_count: number;
};

const apiBase =
  process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/$/, '') ||
  'http://localhost:8000/api';

export type CertificateImageFormat = 'png' | 'jpg';

async function unwrap<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const payload = await response.json().catch(() => ({}));
    const detail = payload?.detail || 'Request failed.';
    throw new Error(detail);
  }
  return (await response.json()) as T;
}

export async function fetchTemplates(): Promise<CertificateTemplate[]> {
  const response = await fetch(`${apiBase}/templates`, { cache: 'no-store' });
  return unwrap<CertificateTemplate[]>(response);
}

export async function generateCertificate(input: {
  template_id: string;
  payload: CertificatePayload;
}): Promise<CertificateRecord> {
  const response = await fetch(`${apiBase}/certificates/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(input),
  });
  return unwrap<CertificateRecord>(response);
}

export async function bulkGenerate(input: {
  template_id: string;
  file: File;
  issuer_name?: string;
  issuer_signature_file?: File;
}): Promise<BulkGenerationResponse> {
  const formData = new FormData();
  formData.append('template_id', input.template_id);
  if (input.issuer_name?.trim()) {
    formData.append('issuer_name', input.issuer_name.trim());
  }
  if (input.issuer_signature_file) {
    formData.append('issuer_signature_file', input.issuer_signature_file);
  }
  formData.append('file', input.file);

  const response = await fetch(`${apiBase}/certificates/bulk`, {
    method: 'POST',
    body: formData,
  });
  return unwrap<BulkGenerationResponse>(response);
}

function _extractFilename(contentDisposition: string | null, fallback: string): string {
  if (!contentDisposition) {
    return fallback;
  }

  const utf8Match = contentDisposition.match(/filename\*=UTF-8''([^;]+)/i);
  if (utf8Match?.[1]) {
    return decodeURIComponent(utf8Match[1]);
  }

  const normalMatch = contentDisposition.match(/filename="?([^\";]+)"?/i);
  if (normalMatch?.[1]) {
    return normalMatch[1];
  }

  return fallback;
}

export async function downloadBulkCertificatesZip(input: {
  certificate_ids: string[];
  format?: CertificateImageFormat;
}): Promise<BulkZipDownloadResponse> {
  const response = await fetch(`${apiBase}/certificates/bulk/download`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      certificate_ids: input.certificate_ids,
      format: input.format ?? 'png',
    }),
  });

  if (!response.ok) {
    const payload = await response.json().catch(() => ({}));
    const detail = payload?.detail || 'Bulk ZIP download failed.';
    throw new Error(detail);
  }

  const blob = await response.blob();
  const filename = _extractFilename(
    response.headers.get('content-disposition'),
    'bulk-certificates.zip'
  );
  const generatedCountHeader = response.headers.get('x-generated-count');
  const generatedCount = generatedCountHeader ? Number(generatedCountHeader) : input.certificate_ids.length;

  return {
    blob,
    filename,
    generated_count: Number.isFinite(generatedCount) ? generatedCount : input.certificate_ids.length,
  };
}

export async function verifyCertificate(certificateId: string): Promise<VerificationResponse> {
  const response = await fetch(`${apiBase}/verify/${encodeURIComponent(certificateId)}`, {
    cache: 'no-store',
  });
  return unwrap<VerificationResponse>(response);
}

export function buildCertificateDownloadUrl(
  certificateId: string,
  format: CertificateImageFormat = 'png'
): string {
  return `${apiBase}/certificates/${encodeURIComponent(certificateId)}/download?format=${format}`;
}
