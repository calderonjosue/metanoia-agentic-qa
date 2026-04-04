'use client'

import { useState } from 'react'

export default function Checkout() {
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)

  const handleCheckout = async () => {
    setLoading(true)
    setError(null)
    
    try {
      const response = await fetch('http://localhost:8000/checkout', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: 'demo-user',
          items: [
            { product_id: 1, quantity: 1 },
            { product_id: 2, quantity: 2 }
          ]
        })
      })
      
      if (!response.ok) throw new Error('Checkout failed')
      const data = await response.json()
      setResult(data)
    } catch (err) {
      setError('Failed to process checkout. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <h1>Checkout</h1>
      
      {!result && !error && (
        <div style={{ marginTop: '1rem' }}>
          <div style={{ padding: '1rem', background: '#f5f5f5', borderRadius: '8px', marginBottom: '1rem' }}>
            <h3>Order Summary</h3>
            <p>Laptop Pro 15 x 1 - $1,299.99</p>
            <p>Wireless Mouse x 2 - $59.98</p>
            <hr style={{ margin: '0.5rem 0' }} />
            <p style={{ fontWeight: 'bold' }}>Total: $1,359.97</p>
          </div>
          
          <button 
            onClick={handleCheckout}
            disabled={loading}
            style={{ 
              padding: '1rem 2rem', 
              fontSize: '1rem',
              background: loading ? '#666' : '#1a1a1a', 
              color: 'white', 
              border: 'none', 
              borderRadius: '4px',
              cursor: loading ? 'not-allowed' : 'pointer'
            }}
          >
            {loading ? 'Processing...' : 'Place Order'}
          </button>
        </div>
      )}
      
      {result && (
        <div style={{ marginTop: '1rem', padding: '1rem', background: '#d4edda', borderRadius: '8px', color: '#155724' }}>
          <h2>Order Confirmed!</h2>
          <p><strong>Order ID:</strong> {result.order_id}</p>
          <p><strong>Status:</strong> {result.status}</p>
          <p><strong>Total:</strong> ${result.total}</p>
          <p><strong>Created:</strong> {result.created_at}</p>
        </div>
      )}
      
      {error && (
        <div style={{ marginTop: '1rem', padding: '1rem', background: '#f8d7da', borderRadius: '8px', color: '#721c24' }}>
          {error}
        </div>
      )}
    </div>
  )
}
