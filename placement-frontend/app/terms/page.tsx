import { LegalPageLayout } from '@/components/LegalPageLayout';

export const metadata = { title: 'Terms & Conditions' };

export default function TermsPage() {
  return (
    <LegalPageLayout title="Terms & Conditions">
      {`Welcome to Shukl Placement OS. By using our portal, you agree to the following:

Clause 7 (Student Consent): your data is used for analytics only in anonymized form. See our Privacy Policy for the full clause.

Clause 8 (Tenant Consent): companies and colleges may not misuse student data. See our Tenant Agreement for the full clause.

By creating an account, you confirm you have read and accepted the relevant clause for your role.`}
    </LegalPageLayout>
  );
}
