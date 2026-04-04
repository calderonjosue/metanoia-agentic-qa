export default function Home() {
  return (
    <div>
      <h1>Welcome to Metanoia E-Commerce Demo</h1>
      <p>This is a sample e-commerce application for testing the Metanoia-QA system.</p>
      <div style={{ marginTop: '2rem' }}>
        <h2>Quick Links</h2>
        <ul style={{ lineHeight: '2' }}>
          <li><a href="/products">Browse Products</a></li>
          <li><a href="/cart">View Cart</a></li>
          <li><a href="/checkout">Checkout</a></li>
        </ul>
      </div>
      <div style={{ marginTop: '2rem', padding: '1rem', background: '#f5f5f5', borderRadius: '8px' }}>
        <h3>Demo Features</h3>
        <ul>
          <li>Product listing and search</li>
          <li>Shopping cart functionality</li>
          <li>Checkout flow</li>
          <li>API health monitoring</li>
        </ul>
      </div>
    </div>
  )
}
