import React from 'react';
import './globals.css';

export const metadata = {
  title: 'RAGEdu',
  description: 'Course material search with page citations'
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
