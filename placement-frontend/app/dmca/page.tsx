import { LegalPageLayout } from '@/components/LegalPageLayout';

export const metadata = { title: 'DMCA Policy' };

export default function DmcaPage() {
  return (
    <LegalPageLayout title="DMCA Policy">
      {`All Learn videos are embedded from YouTube via the YouTube API — we do not host any video ourselves. If you are a content owner and have a concern, contact us at support@placement.com and we will remove the embed within 24 hours.

For job descriptions, we are not responsible for company-submitted content. If you find a fake job listing, please report it via Support.`}
    </LegalPageLayout>
  );
}
