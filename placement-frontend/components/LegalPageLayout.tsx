import Link from 'next/link';
import React from 'react';

export function LegalPageLayout({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-gray-50 py-10">
      <div className="container mx-auto px-4 max-w-3xl">
        <Link href="/" className="text-blue-600 hover:underline text-sm">&larr; Back to home</Link>
        <div className="bg-white p-8 rounded-lg shadow-md mt-4">
          <h1 className="text-2xl font-bold mb-6">{title}</h1>
          <div className="prose prose-sm max-w-none text-gray-700 whitespace-pre-line leading-relaxed">
            {children}
          </div>
        </div>
      </div>
    </div>
  );
}
