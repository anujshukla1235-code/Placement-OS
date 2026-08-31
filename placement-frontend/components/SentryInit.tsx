'use client';

import * as Sentry from '@sentry/react';
import { useEffect } from 'react';

export default function SentryInit() {
  useEffect(() => {
    try {
      const dsn = process.env.NEXT_PUBLIC_SENTRY_DSN;
      if (!dsn) return;

      Sentry.init({
        dsn,
        environment: process.env.NEXT_PUBLIC_SENTRY_ENVIRONMENT || process.env.NODE_ENV,
        tracesSampleRate: Number(process.env.NEXT_PUBLIC_SENTRY_TRACES_SAMPLE_RATE || 0) || 0,
      });
    } catch (e) {
      // ignore init errors in environments without Sentry installed
      // console.error('Sentry init failed', e);
    }
  }, []);

  return null;
}
