#!/usr/bin/env python3
"""
Migrate data from SQLite to MongoDB
Run this script to transfer all data from farmer_app.db to MongoDB
"""

import sqlite3
from pymongo import MongoClient
from bson import ObjectId
from werkzeug.security import generate_password_hash
from datetime import datetime
import sys

def migrate_to_mongodb():
    """Migrate SQLite data to MongoDB"""
    
    # Connect to MongoDB
    try:
        mongo_client = MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=5000)
        mongo_client.admin.command('ping')
        mongo_db = mongo_client['farmer_app']
        print("✓ Connected to MongoDB")
    except Exception as e:
        print(f"✗ MongoDB connection failed: {e}")
        print("Please make sure MongoDB is running on localhost:27017")
        return False
    
    # Connect to SQLite
    try:
        sqlite_conn = sqlite3.connect('farmer_app.db')
        sqlite_conn.row_factory = sqlite3.Row
        sqlite_cur = sqlite_conn.cursor()
        print("✓ Connected to SQLite")
    except Exception as e:
        print(f"✗ SQLite connection failed: {e}")
        return False
    
    # Clear existing MongoDB data
    print("\nClearing existing data...")
    mongo_db.users.delete_many({})
    mongo_db.products.delete_many({})
    mongo_db.cart.delete_many({})
    mongo_db.orders.delete_many({})
    mongo_db.order_items.delete_many({})
    users_count = 0
    products_count = 0
    orders_count = 0
    
    try:
        # Migrate users
        print("\nMigrating users...")
        sqlite_cur.execute("SELECT * FROM users")
        users = sqlite_cur.fetchall()
        user_id_map = {}
        
        for user in users:
            mongo_doc = {
                'name': user['name'],
                'email': user['email'],
                'password': user['password'],  # already hashed
                'role': user['role'],
                'phone': user['phone'],
                'address': user['address'],
                'created_at': datetime.fromisoformat(user['created_at']) if user['created_at'] else datetime.now()
            }
            result = mongo_db.users.insert_one(mongo_doc)
            user_id_map[user['id']] = result.inserted_id
            users_count += 1
        
        print(f"✓ Migrated {users_count} users")
        
        # Migrate products
        print("Migrating products...")
        sqlite_cur.execute("SELECT * FROM products")
        products = sqlite_cur.fetchall()
        
        for product in products:
            farmer_id = user_id_map.get(product['farmer_id'])
            if not farmer_id:
                print(f"  ⚠ Skipping product {product['name']} - farmer not found")
                continue
            
            mongo_doc = {
                'farmer_id': farmer_id,
                'name': product['name'],
                'price': product['price'],
                'quantity': product['quantity'],
                'unit': product['unit'] if product['unit'] else 'kg',
                'category': product['category'] if product['category'] else 'Vegetables',
                'description': product['description'] if product['description'] else '',
                'image': product['image'] if product['image'] else '',
                'created_at': datetime.fromisoformat(product['created_at']) if product['created_at'] else datetime.now()
            }
            mongo_db.products.insert_one(mongo_doc)
            products_count += 1
        
        print(f"✓ Migrated {products_count} products")
        
        # Migrate orders
        print("Migrating orders...")
        sqlite_cur.execute("SELECT * FROM orders")
        orders = sqlite_cur.fetchall()
        order_id_map = {}
        
        for order in orders:
            customer_id = user_id_map.get(order['customer_id'])
            if not customer_id:
                print(f"  ⚠ Skipping order {order['id']} - customer not found")
                continue
            
            mongo_doc = {
                'customer_id': customer_id,
                'total_price': order['total_price'],
                'status': order['status'],
                'payment_method': order['payment_method'],
                'delivery_date': order['delivery_date'],
                'created_at': datetime.fromisoformat(order['created_at']) if order['created_at'] else datetime.now()
            }
            result = mongo_db.orders.insert_one(mongo_doc)
            order_id_map[order['id']] = result.inserted_id
            orders_count += 1
        
        print(f"✓ Migrated {orders_count} orders")
        
        # Migrate order items
        print("Migrating order items...")
        sqlite_cur.execute("SELECT * FROM order_items")
        order_items = sqlite_cur.fetchall()
        order_items_count = 0
        
        for item in order_items:
            order_id = order_id_map.get(item['order_id'])
            product_id = None
            farmer_id = None
            
            # Find product in MongoDB
            sqlite_cur.execute("SELECT farmer_id FROM products WHERE id = ?", (item['product_id'],))
            prod = sqlite_cur.fetchone()
            if prod:
                farmer_id = user_id_map.get(prod['farmer_id'])
                # Find product by name and farmer
                product = mongo_db.products.find_one({
                    'farmer_id': farmer_id,
                    'name': item['product_name']
                })
                if product:
                    product_id = product['_id']
            
            if not order_id or not product_id:
                continue
            
            mongo_doc = {
                'order_id': order_id,
                'product_id': product_id,
                'product_name': item['product_name'],
                'quantity': item['quantity'],
                'price': item['price'],
                'farmer_id': farmer_id
            }
            mongo_db.order_items.insert_one(mongo_doc)
            order_items_count += 1
        
        print(f"✓ Migrated {order_items_count} order items")
        
        # Create indexes
        print("\nCreating indexes...")
        mongo_db.users.create_index('email', unique=True)
        mongo_db.products.create_index('farmer_id')
        mongo_db.orders.create_index('customer_id')
        mongo_db.order_items.create_index([('order_id', 1), ('farmer_id', 1)])
        print("✓ Indexes created")
        
        print("\n" + "="*60)
        print("MIGRATION COMPLETED SUCCESSFULLY!")
        print("="*60)
        print(f"Users: {users_count}")
        print(f"Products: {products_count}")
        print(f"Orders: {orders_count}")
        print(f"Order Items: {order_items_count}")
        print("="*60 + "\n")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        sqlite_conn.close()
        mongo_client.close()

if __name__ == "__main__":
    success = migrate_to_mongodb()
    sys.exit(0 if success else 1)
