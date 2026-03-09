import { VerifyLanding } from '@/components/VerifyLanding';

export default function HomePage() {
  return (
    <main>
      <section className="hero">
        <h1>Certificate Verification</h1>
        <p>Scan the QR code or paste the certificate ID to confirm authenticity.</p>
      </section>
      <div className="grid">
        <VerifyLanding />
      </div>
    </main>
  );
}
