import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Dig Deep Fitness Platform',
  description: 'Premium fitness platform for coaches and clients to maximize progress',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
