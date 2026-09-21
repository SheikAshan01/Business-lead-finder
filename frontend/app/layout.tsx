import './globals.css';
import type { Metadata } from 'next';
export const metadata: Metadata = { title:'SRA Business Lead Finder', description:'Find. Verify. Connect.' };
export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) { return <html lang="en"><body>{children}</body></html>; }
