from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import random
from datetime import datetime

app = FastAPI(title="E-Commerce Demo API", version="1.0.0")

PRODUCTS = [
    {"id": 1, "name": "Laptop Pro 15", "price": 1299.99, "category": "electronics", "stock": 25},
    {"id": 2, "name": "Wireless Mouse", "price": 29.99, "category": "electronics", "stock": 150},
    {"id": 3, "name": "USB-C Hub", "price": 49.99, "category": "electronics", "stock": 75},
    {"id": 4, "name": "Mechanical Keyboard", "price": 89.99, "category": "electronics", "stock": 60},
    {"id": 5, "name": "Monitor 27 inch", "price": 349.99, "category": "electronics", "stock": 30},
    {"id": 6, "name": "Webcam HD", "price": 79.99, "category": "electronics", "stock": 45},
    {"id": 7, "name": "Desk Lamp", "price": 24.99, "category": "home", "stock": 100},
    {"id": 8, "name": "Notebook Set", "price": 12.99, "category": "office", "stock": 200},
]

CARTS = {}

class CheckoutItem(BaseModel):
    product_id: int
    quantity: int

class CheckoutRequest(BaseModel):
    user_id: str
    items: List[CheckoutItem]

class OrderResponse(BaseModel):
    order_id: str
    status: str
    total: float
    items: List[dict]
    created_at: str

@app.get("/")
async def root():
    return {"message": "E-Commerce Demo API", "version": "1.0.0"}

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/products")
async def list_products(category: Optional[str] = None):
    if category:
        return [p for p in PRODUCTS if p["category"] == category]
    return PRODUCTS

@app.get("/products/{product_id}")
async def get_product(product_id: int):
    product = next((p for p in PRODUCTS if p["id"] == product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@app.post("/checkout")
async def checkout(request: CheckoutRequest) -> OrderResponse:
    if not request.items:
        raise HTTPException(status_code=400, detail="No items in cart")
    
    order_items = []
    total = 0.0
    
    for item in request.items:
        product = next((p for p in PRODUCTS if p["id"] == item.product_id), None)
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")
        if product["stock"] < item.quantity:
            raise HTTPException(status_code=400, detail=f"Insufficient stock for {product['name']}")
        
        item_total = product["price"] * item.quantity
        total += item_total
        order_items.append({
            "product_id": product["id"],
            "name": product["name"],
            "price": product["price"],
            "quantity": item.quantity,
            "subtotal": item_total
        })
    
    order_id = f"ORD-{random.randint(10000, 99999)}"
    
    return OrderResponse(
        order_id=order_id,
        status="confirmed",
        total=round(total, 2),
        items=order_items,
        created_at=datetime.now().isoformat()
    )

@app.get("/categories")
async def list_categories():
    categories = list(set(p["category"] for p in PRODUCTS))
    return {"categories": categories}
