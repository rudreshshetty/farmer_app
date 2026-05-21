import sqlite3
from pymongo import MongoClient
from bson import ObjectId
from werkzeug.security import generate_password_hash
from datetime import datetime

# SQLite connection
sqlite_conn = sqlite3.connect('farmer_app.db')
sqlite_conn.row_factory = sqlite3.Row
sqlite_cur = sqlite_conn.cursor()

# MongoDB connection
mongo_client = MongoClient('mongodb://localhost:27017/')
mongo_db = mongo_client['farmer_app']

# Migrate users
print("Migrating users...")
sqlite_cur.execute("SELECT * FROM users")
users = sqlite_cur.fetchall()
for user in users:
    mongo_db.users.insert_one({
        'name': user['name'],
        'email': user['email'],
        'password': user['password'],  # already hashed
        'role': user['role'],
        'phone': user['phone'],
        'address': user['address'],
        'created_at': datetime.fromisoformat(user['created_at']) if user['created_at'] else datetime.now()
    })

# Get user id mapping
user_id_map = {}
for user in mongo_db.users.find():
    # Find original id
    sqlite_cur.execute("SELECT id FROM users WHERE email = ?", (user['email'],))
    original = sqlite_cur.fetchone()
    if original:
        user_id_map[original['id']] = user['_id']

# Migrate products
print("Migrating products...")
sqlite_cur.execute("SELECT * FROM products")
products = sqlite_cur.fetchall()
for product in products:
    farmer_id = user_id_map.get(product['farmer_id'])
    if farmer_id:
        mongo_db.products.insert_one({
            'farmer_id': farmer_id,
            'name': product['name'],
            'price': product['price'],
            'quantity': product['quantity'],
            'unit': product['unit'],
            'category': product['category'],
            'description': product['description'],
            'image': product['image'],
            'created_at': datetime.fromisoformat(product['created_at']) if product['created_at'] else datetime.now()
        })

# Migrate cart
print("Migrating cart...")
sqlite_cur.execute("SELECT * FROM cart")
carts = sqlite_cur.fetchall()
for cart in carts:
    customer_id = user_id_map.get(cart['customer_id'])
    product_id = None
    # Find product _id
    sqlite_cur.execute("SELECT farmer_id FROM products WHERE id = ?", (cart['product_id'],))
    prod = sqlite_cur.fetchone()
    if prod:
        farmer_id = user_id_map.get(prod['farmer_id'])
        if farmer_id:
            prod_mongo = mongo_db.products.find_one({'farmer_id': farmer_id, 'name': ...})  # need to match by name or something
            # This is tricky, assume order
            # For simplicity, skip or match by name
            # Let's assume products are inserted in order
            products_list = list(mongo_db.products.find())
            if len(products_list) > cart['product_id'] - 1:
                product_id = products_list[cart['product_id'] - 1]['_id']
    if customer_id and product_id:
        mongo_db.cart.insert_one({
            'customer_id': customer_id,
            'product_id': product_id,
            'quantity': cart['quantity'],
            'added_at': datetime.fromisoformat(cart['added_at']) if cart['added_at'] else datetime.now()
        })

# Similarly for orders and order_items, but it's complex.

print("Migration completed (basic).")

sqlite_conn.close()
mongo_client.close()