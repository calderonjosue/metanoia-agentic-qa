'use client'

import { useState } from 'react'

interface CartItem {
  id: number
  name: string
  price: number
  quantity: number
}

const MOCK_CART: CartItem[] = [
  { id: 1, name: 'Laptop Pro 15', price: 1299.99, quantity: 1 },
  { id: 2, name: 'Wireless Mouse', price: 29.99, quantity: 2 },
]

export default function Cart() {
  const [cart] = useState<CartItem[]>(MOCK_CART)

  const total = cart.reduce((sum, item) => sum + item.price * item.quantity, 0)

  return (
    <div>
      <h1>Shopping Cart</h1>
      {cart.length === 0 ? (
        <p>Your cart is empty.</p>
      ) : (
        <>
          <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: '1rem' }}>
            <thead>
              <tr style={{ borderBottom: '2px solid #ddd' }}>
                <th style={{ textAlign: 'left', padding: '0.5rem' }}>Product</th>
                <th style={{ textAlign: 'right', padding: '0.5rem' }}>Price</th>
                <th style={{ textAlign: 'center', padding: '0.5rem' }}>Quantity</th>
                <th style={{ textAlign: 'right', padding: '0.5rem' }}>Subtotal</th>
              </tr>
            </thead>
            <tbody>
              {cart.map(item => (
                <tr key={item.id} style={{ borderBottom: '1px solid #eee' }}>
                  <td style={{ padding: '0.5rem' }}>{item.name}</td>
                  <td style={{ textAlign: 'right', padding: '0.5rem' }}>${item.price}</td>
                  <td style={{ textAlign: 'center', padding: '0.5rem' }}>{item.quantity}</td>
                  <td style={{ textAlign: 'right', padding: '0.5rem' }}>${(item.price * item.quantity).toFixed(2)}</td>
                </tr>
              ))}
            </tbody>
          </table>
          <div style={{ marginTop: '1rem', textAlign: 'right', fontSize: '1.25rem', fontWeight: 'bold' }}>
            Total: ${total.toFixed(2)}
          </div>
          <div style={{ marginTop: '1rem', textAlign: 'right' }}>
            <a 
              href="/checkout"
              style={{ 
                display: 'inline-block',
                padding: '0.75rem 1.5rem', 
                background: '#1a1a1a', 
                color: 'white', 
                textDecoration: 'none', 
                borderRadius: '4px'
              }}
            >
              Proceed to Checkout
            </a>
          </div>
        </>
      )}
    </div>
  )
}
