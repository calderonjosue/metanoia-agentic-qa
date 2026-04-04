import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Metanoia E-Commerce Demo',
  description: 'Sample e-commerce application for QA testing',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body style={{ margin: 0, fontFamily: 'system-ui, sans-serif' }}>
        <nav style={{ padding: '1rem', background: '#1a1a1a', color: 'white' }}>
          <div style={{ maxWidth: '1200px', margin: '0 auto', display: 'flex', gap: '2rem' }}>
            <a href="/" style={{ color: 'white', textDecoration: 'none', fontWeight: 'bold' }}>Home</a>
            <a href="/products" style={{ color: 'white', textDecoration: 'none' }}>Products</a>
            <a href="/cart" style={{ color: 'white', textDecoration: 'none' }}>Cart</a>
            <a href="/checkout" style={{ color: 'white', textDecoration: 'none' }}>Checkout</a>
          </div>
        </nav>
        <main style={{ maxWidth: '1200px', margin: '0 auto', padding: '2rem' }}>
          {children}
        </main>
      </body>
    </html>
  )
}
