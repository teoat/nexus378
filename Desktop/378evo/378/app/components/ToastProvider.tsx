// app/components/ToastProvider.tsx
"use client"; // Required for Next.js App Router to know this is a client component

import React from 'react';
import { Toaster } from 'react-hot-toast';

/**
 * This component provides the context for toast notifications.
 * It should be placed at the root of your application layout
 * (e.g., in app/pages/_app.tsx or app/layout.tsx) so that
 * notifications can be displayed anywhere in the app.
 */
export function ToastProvider({ children }: { children: React.ReactNode }) {
  return (
    <>
      {children}
      <Toaster 
        position="bottom-right"
        toastOptions={{
          duration: 5000,
          style: {
            background: '#363636',
            color: '#fff',
          },
        }}
      />
    </>
  );
}