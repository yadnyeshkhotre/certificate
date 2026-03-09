'use client';

import { Suspense } from 'react';
import { useSearchParams } from 'next/navigation';

import { VerifyForm } from '@/components/VerifyForm';

function VerifyByQuery() {
  const searchParams = useSearchParams();
  const certificateId = searchParams.get('certificateId') || '';

  return <VerifyForm defaultCertificateId={certificateId} autoCheck />;
}

export function VerifyLanding() {
  return (
    <Suspense fallback={<div className="panel">Loading verification...</div>}>
      <VerifyByQuery />
    </Suspense>
  );
}
