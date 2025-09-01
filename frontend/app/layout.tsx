import React from 'react';
import './globals.css';

export const metadata = {
  title: 'RAGEdu',
  description: 'Course-grounded Q&A with citations (stubbed)'
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <head />
      <body>
        {children}
      </body>
    </html>
  );
}
