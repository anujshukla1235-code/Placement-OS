import { LegalPageLayout } from '@/components/LegalPageLayout';

export const metadata = { title: 'About Us' };

export default function AboutPage() {
  return (
    <LegalPageLayout title="About Us">
      {`We help students get placed for free — a cloud, AI, and blockchain-powered placement OS built by Anuj Placementa, run on a zero-cost architecture.`}
    </LegalPageLayout>
  );
}
