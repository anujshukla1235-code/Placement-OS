import { LegalPageLayout } from '@/components/LegalPageLayout';

export const metadata = { title: 'Privacy Policy | Clause 7' };

export default function PrivacyPage() {
  return (
    <LegalPageLayout title="Clause 7: Student Data Consent & Privacy">
      {`By ticking the checkbox at signup, you (Student) agree that:

1. You provide your resume, phone, email voluntarily for placement purposes.
2. Your anonymized data (skills, ATS score, without your name) can be used to show analytics to companies.
3. Your full resume and contact details will ONLY be shared with a company when you apply to their job. We will not sell your data.
4. We store your data securely (PostgreSQL + Cloudinary). You can request deletion via Contact Us.
5. We will send you job notifications via email/WhatsApp.`}
    </LegalPageLayout>
  );
}
