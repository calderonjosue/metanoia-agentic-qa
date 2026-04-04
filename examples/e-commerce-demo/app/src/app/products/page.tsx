'use client'

import { useState, useEffect } from 'react'

interface Product {
  id: number
  name: string
  price: number
  category: string
  stock: number
}

export default function Products() {
  const [products, setProducts] = useState<Product[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch('http://localhost:8000/products')
      .then(res => res.json())
      .then(data => {
        setProducts(data)
        setLoading(false)
      })
      .catch(() => setLoading(false))
  }, [])

  if (loading) return <div>Loading products...</div>

  return (
    <div>
      <h1>Products</h1>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(250px, 1fr))', gap: '1rem', marginTop: '1rem' }}>
        {products.map(product => (
          <div key={product.id} style={{ border: '1px solid #ddd', borderRadius: '8px', padding: '1rem' }}>
            <h3>{product.name}</h3>
            <p style={{ color: '#666' }}>{product.category}</p>
            <p style={{ fontWeight: 'bold', fontSize: '1.25rem' }}>${product.price}</p>
            <p style={{ fontSize: '0.875rem', color: product.stock > 10 ? 'green' : 'orange' }}>
              {product.stock > 10 ? 'In Stock' : `Only ${product.stock} left`}
            </p>
            <button 
              onClick={() => window.location.href = '/cart'}
              style={{ 
                marginTop: '0.5rem', 
                padding: '0.5rem 1rem', 
                background: '#1a1a1a', 
                color: 'white', 
                border: 'none', 
                borderRadius: '4px',
                cursor: 'pointer'
              }}
            >
              Add to Cart
            </button>
          </div>
        ))}
      </div>
    </div>
  )
}
