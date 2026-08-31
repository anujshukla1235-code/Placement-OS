import { LegalPageLayout } from '@/components/LegalPageLayout';

export const metadata = { title: 'Contact Us' };

export default function ContactPage() {
  return (
    <LegalPageLayout title="Contact Us">
      {`Have a question, issue, or a fake job listing to report? Email us at support@placement.com and we'll get back to you.\n\n(An in-app support ticket form is planned — for now, email is the fastest way to reach us.)`}
    </LegalPageLayout>
  );
}
