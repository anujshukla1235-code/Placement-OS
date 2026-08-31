import { LegalPageLayout } from '@/components/LegalPageLayout';

export const metadata = { title: 'Tenant Agreement | Clause 8' };

export default function TenantAgreementPage() {
  return (
    <LegalPageLayout title="Clause 8: Tenant / Company / College Data Consent">
      {`By registering as a tenant (Company or College), you agree that:

1. All job details and company information you provide is authentic. We may verify via LinkedIn/your website.
2. You will NOT misuse student data (resume, phone, email). It may only be used for hiring — spam or marketing use is strictly prohibited and will lead to a permanent ban.
3. You must provide a valid rejection reason when rejecting a student. Blank rejections are not allowed.
4. Student data must be deleted from your systems after the hiring process ends, if the student requests it.`}
    </LegalPageLayout>
  );
}
