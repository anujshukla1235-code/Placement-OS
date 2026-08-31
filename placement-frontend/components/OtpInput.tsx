'use client';

import React, { useEffect, useRef } from 'react';

type OtpInputProps = {
  length?: number;
  value: string;
  onChange: (value: string) => void;
  autoFocus?: boolean;
  className?: string;
};

export default function OtpInput({ length = 6, value, onChange, autoFocus = false, className = '' }: OtpInputProps) {
  const inputsRef = useRef<Array<HTMLInputElement | null>>([]);

  useEffect(() => {
    if (autoFocus && inputsRef.current[0]) {
      inputsRef.current[0].focus();
    }
  }, [autoFocus]);

  const handleChange = (index: number, val: string) => {
    const sanitized = val.replace(/[^0-9]/g, '');
    const chars = value.split('');
    chars[index] = sanitized ? sanitized[0] : '';
    const next = chars.slice(0, length).join('').padEnd(length, '');
    onChange(next);

    if (sanitized && inputsRef.current[index + 1]) {
      inputsRef.current[index + 1]?.focus();
      inputsRef.current[index + 1]?.select();
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>, idx: number) => {
    if (e.key === 'Backspace' && !value[idx] && idx > 0) {
      inputsRef.current[idx - 1]?.focus();
      const chars = value.split('');
      chars[idx - 1] = '';
      onChange(chars.join(''));
    }
    if (e.key === 'ArrowLeft' && idx > 0) {
      inputsRef.current[idx - 1]?.focus();
    }
    if (e.key === 'ArrowRight' && idx < length - 1) {
      inputsRef.current[idx + 1]?.focus();
    }
  };

  const handlePaste = (e: React.ClipboardEvent<HTMLInputElement>) => {
    e.preventDefault();
    const paste = e.clipboardData.getData('text').replace(/\s+/g, '');
    const digits = paste.replace(/[^0-9]/g, '').slice(0, length).split('');
    const next = Array.from({ length }).map((_, i) => digits[i] ?? '');
    onChange(next.join(''));
  };

  return (
    <div className={`flex gap-2 ${className}`}>
      {Array.from({ length }).map((_, idx) => (
        <input
          key={idx}
          ref={(el) => { inputsRef.current[idx] = el; }}
          type="text"
          inputMode="numeric"
          maxLength={1}
          value={value[idx] ?? ''}
          onChange={(e) => handleChange(idx, e.target.value)}
          onKeyDown={(e) => handleKeyDown(e, idx)}
          onPaste={handlePaste}
          className="w-12 h-12 text-center border rounded-md focus:ring-2 focus:ring-blue-400"
          aria-label={`OTP digit ${idx + 1}`}
        />
      ))}
    </div>
  );
}
