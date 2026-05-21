#!/usr/bin/env python3
"""
Complete Inventory Display - Shows ALL vegetables with full details
"""

from pymongo import MongoClient
from datetime import datetime
import tabulate

# MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client['farmer_app']

print("\n" + "="*150)
print("COMPLETE FARMER APP INVENTORY - ALL DATA SUMMARY".center(150))
print("="*150)

# 1. VEGETABLES COUNT
products = list(db.products.find().sort("name", 1))
print(f"\n📦 TOTAL VEGETABLES INSERTED: {len(products)}")
print("-"*150)

# 2. GROUP BY FARMER
farmers_data = {}
for product in products:
    farmer_id = str(product.get('farmer_id', ''))
    farmer = db.users.find_one({'_id': product.get('farmer_id')})
    farmer_name = farmer.get('name', 'Unknown') if farmer else 'Unknown'
    
    if farmer_name not in farmers_data:
        farmers_data[farmer_name] = []
    farmers_data[farmer_name].append(product)

# 3. DETAILED TABLE
table_data = []
for i, product in enumerate(products, 1):
    farmer = db.users.find_one({'_id': product.get('farmer_id')})
    farmer_name = farmer.get('name', 'Unknown') if farmer else 'Unknown'
    
    table_data.append([
        i,
        product.get('name', 'N/A'),
        farmer_name,
        f"₹{product.get('price', 0):.2f}",
        f"{product.get('quantity', 0):.1f} kg",
        f"₹{product.get('quantity', 0) * product.get('price', 0):.2f}",
        product.get('category', 'Vegetables'),
        str(product.get('_id'))[:12] + "..."
    ])

headers = ["#", "Vegetable Name", "Farmer", "Price/kg", "Stock", "Total Value", "Category", "Product ID"]
print(tabulate.tabulate(table_data, headers=headers, tablefmt="grid"))

# 4. SUMMARY BY FARMER
print("\n" + "="*150)
print("VEGETABLES BY FARMER".center(150))
print("="*150)

farmer_summary = []
total_value = 0
total_stock = 0

for farmer_name in sorted(farmers_data.keys()):
    products_list = farmers_data[farmer_name]
    farmer_stock = sum(p.get('quantity', 0) for p in products_list)
    farmer_value = sum(p.get('quantity', 0) * p.get('price', 0) for p in products_list)
    total_stock += farmer_stock
    total_value += farmer_value
    
    farmer_summary.append([
        farmer_name,
        len(products_list),
        f"{farmer_stock:.1f} kg",
        f"₹{farmer_value:.2f}"
    ])

print(tabulate.tabulate(farmer_summary, 
                       headers=["Farmer Name", "# Products", "Total Stock", "Total Value"],
                       tablefmt="grid"))

# 5. OVERALL STATISTICS
print("\n" + "="*150)
print("📊 OVERALL STATISTICS".center(150))
print("="*150)

users = list(db.users.find())
orders = list(db.orders.find())
order_items = list(db.order_items.find())

stats = [
    ["Total Farmers", len([u for u in users if u.get('role') == 'farmer'])],
    ["Total Customers", len([u for u in users if u.get('role') == 'customer'])],
    ["Total Products/Vegetables", len(products)],
    ["Total Stock Quantity", f"{total_stock:.1f} kg"],
    ["Total Inventory Value", f"₹{total_value:.2f}"],
    ["Total Orders", len(orders)],
    ["Total Order Items", len(order_items)],
]

print(tabulate.tabulate(stats, headers=["Metric", "Value"], tablefmt="grid"))

# 6. PRICE RANGE
prices = [p.get('price', 0) for p in products]
print("\n" + "-"*150)
print(f"Lowest Price: ₹{min(prices):.2f}/kg")
print(f"Highest Price: ₹{max(prices):.2f}/kg")
print(f"Average Price: ₹{sum(prices)/len(prices):.2f}/kg")
print("-"*150)

# 7. DETAILED VEGETABLE LIST WITH UPDATE LINKS
print("\n" + "="*150)
print("COMPLETE VEGETABLE LIST WITH EDIT OPTIONS".center(150))
print("="*150 + "\n")

for i, product in enumerate(products, 1):
    farmer = db.users.find_one({'_id': product.get('farmer_id')})
    farmer_name = farmer.get('name', 'Unknown') if farmer else 'Unknown'
    
    print(f"{i}. {product.get('name', 'N/A').upper()}")
    print(f"   Farmer: {farmer_name}")
    print(f"   Price: ₹{product.get('price', 0):.2f} per kg")
    print(f"   Stock: {product.get('quantity', 0):.1f} kg")
    print(f"   Category: {product.get('category', 'Vegetables')}")
    print(f"   Description: {product.get('description', 'N/A')}")
    print(f"   Value: ₹{product.get('quantity', 0) * product.get('price', 0):.2f}")
    print(f"   📝 EDIT LINK: http://127.0.0.1:5000/edit_product/{product.get('_id')}")
    print()

print("="*150)
print("\n✅ Dashboard is ready at: http://127.0.0.1:5000/dashboard")
print("🌾 All vegetables with full details are now available for viewing and editing!\n")
