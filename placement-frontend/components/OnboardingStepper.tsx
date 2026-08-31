'use client';

import React from 'react';

type StepperProps = {
  steps: string[];
  current: number;
};

export function OnboardingStepper({ steps, current }: StepperProps) {
  return (
    <div className="w-full max-w-3xl mx-auto mb-6">
      <div className="flex items-center">
        {steps.map((s, idx) => (
          <div key={s} className="flex-1">
            <div className="flex items-center">
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center mr-3 text-white ${
                  idx <= current ? 'bg-blue-600' : 'bg-gray-300'
                }`}
              >
                {idx + 1}
              </div>
              <div className={`text-sm ${idx <= current ? 'text-blue-700' : 'text-gray-500'}`}>{s}</div>
            </div>
            {idx < steps.length - 1 && (
              <div className="h-1 bg-gray-200 mt-3">
                <div
                  style={{ width: '100%' }}
                  className={`h-1 ${idx < current ? 'bg-blue-500' : 'bg-gray-200'}`}
                />
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
