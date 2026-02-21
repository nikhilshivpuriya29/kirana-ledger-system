'use client';

import './globals.css';
import { Inter } from 'next/font/google';
import { useState, useEffect } from 'react';

const inter = Inter({ subsets: ['latin'] });

export const metadata = {
  title: 'बाही-खाता डिजिटल | Bahi-Khata Digital',
  description: 'ग्रामीण खुदरा क्रेडिट और खाता प्रबंधन प्रणाली | Rural Retail Credit & Ledger Management System',
};

interface LayoutProps {
  children: React.ReactNode;
}

export default function RootLayout({ children }: LayoutProps) {
  const [language, setLanguage] = useState<'hi' | 'en'>('hi');

  useEffect(() => {
    // Detect browser language
    const browserLang = navigator.language.startsWith('hi') ? 'hi' : 'en';
    setLanguage(browserLang as 'hi' | 'en');
  }, []);

  return (
    <html lang={language === 'hi' ? 'hi' : 'en'} dir="ltr">
      <head>
        <meta charSet="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Mukta:wght@300;400;600;700&family=Hind:wght@300;400;600;700&display=swap" />
      </head>
      <body className={`${inter.className} bg-gradient-to-br from-orange-50 to-white`}>
        <div className="min-h-screen">
          {/* Header */}
          <header className="sticky top-0 z-50 bg-white border-b border-orange-200 shadow-sm">
            <nav className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-orange-500 rounded-full flex items-center justify-center text-white font-bold">
                  बा
                </div>
                <h1 className="text-2xl font-bold text-orange-600" style={{ fontFamily: 'Mukta, sans-serif' }}>
                  {language === 'hi' ? 'बाही-खाता डिजिटल' : 'Bahi-Khata Digital'}
                </h1>
              </div>
              <button
                onClick={() => setLanguage(language === 'hi' ? 'en' : 'hi')}
                className="px-4 py-2 bg-orange-100 text-orange-600 rounded-lg hover:bg-orange-200 transition font-semibold"
              >
                {language === 'hi' ? 'English' : 'हिंदी'}
              </button>
            </nav>
          </header>

          {/* Main Content */}
          <main className="max-w-7xl mx-auto px-4 py-8">
            {children}
          </main>

          {/* Footer */}
          <footer className="bg-gray-900 text-white py-8 mt-12">
            <div className="max-w-7xl mx-auto px-4 text-center">
              <p style={{ fontFamily: 'Mukta, sans-serif' }} className="text-lg font-semibold">
                {language === 'hi' ? 'बाही-खाता डिजिटल' : 'Bahi-Khata Digital'}
              </p>
              <p className="text-gray-400 mt-2">
                {language === 'hi'
                  ? '© 2024 ग्रामीण खुदरा क्रेडिट प्रबंधन प्रणाली'
                  : '© 2024 Rural Retail Credit Management System'}
              </p>
              <p className="text-gray-500 text-sm mt-4">Built with Next.js, React, FastAPI & MongoDB</p>
            </div>
          </footer>
        </div>
      </body>
    </html>
  );
}
