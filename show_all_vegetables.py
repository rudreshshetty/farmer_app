#!/usr/bin/env python3
"""
Display all vegetables with complete details and update options
"""

from pymongo import MongoClient
from bson import ObjectId
import os

client = MongoClient('mongodb://localhost:27017/')
db = client['farmer_app']

# Get all products
products = list(db.products.find().sort('name', 1))

print('\n' + '='*150)
print('ALL VEGETABLES IN DATABASE - COMPLETE DETAILS WITH UPDATE OPTIONS'.center(150))
print('='*150 + '\n')

# Group by farmer
farmers_dict = {}
for product in products:
    farmer = db.users.find_one({'_id': product['farmer_id']})
    farmer_name = farmer['name'] if farmer else 'Unknown'
    
    if farmer_name not in farmers_dict:
        farmers_dict[farmer_name] = []
    farmers_dict[farmer_name].append(product)

total_value = 0
total_stock_kg = 0

# Display by farmer
for farmer_name, farmer_products in sorted(farmers_dict.items()):
    print(f"\n👨‍🌾 FARMER: {farmer_name.upper()}")
    print(f"   Total Products: {len(farmer_products)}")
    print('-' * 150)
    
    farmer_value = 0
    farmer_stock = 0
    
    for i, product in enumerate(farmer_products, 1):
        item_value = product['price'] * product['quantity']
        farmer_value += item_value
        farmer_stock += product['quantity']
        total_value += item_value
        total_stock_kg += product['quantity']
        
        print(f"\n  {i}. {product['name'].upper()}")
        print(f"     ID: {product['_id']}")
        print(f"     Price: ₹{product['price']:.2f} per {product['unit']}")
        print(f"     Stock: {product['quantity']:.1f} {product['unit']}")
        print(f"     Value: ₹{item_value:.2f}")
        print(f"     Category: {product['category']}")
        print(f"     Description: {product['description']}")
        print(f"     Image URL: {product['image']}")
        
        # Update command
        print(f"     UPDATE: You can edit this in web dashboard at")
        print(f"             http://127.0.0.1:5000/edit_product/{product['_id']}")
    
    print(f"\n     📊 Farmer Summary:")
    print(f"        Total Products: {len(farmer_products)}")
    print(f"        Total Stock: {farmer_stock:.1f} kg")
    print(f"        Total Value: ₹{farmer_value:.2f}")
    print('-' * 150)

print('\n' + '='*150)
print('OVERALL DATABASE SUMMARY'.center(150))
print('='*150)
print(f'\nTotal Farmers: {len(farmers_dict)}')
print(f'Total Products: {len(products)}')
print(f'Total Stock: {total_stock_kg:.1f} kg')
print(f'Total Inventory Value: ₹{total_value:.2f}')
print('\n' + '='*150 + '\n')

print('💡 TO UPDATE ANY VEGETABLE:')
print('   1. Login to web app at http://127.0.0.1:5000')
print('   2. Login as the farmer who owns the product')
print('   3. Click "Edit" button next to the vegetable')
print('   4. Update details and save')
print('   5. Or use this URL: http://127.0.0.1:5000/edit_product/{product_id}\n')
