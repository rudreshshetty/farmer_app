from flask import Flask, render_template, request, redirect, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient
from bson import ObjectId
import os
from datetime import datetime
import qrcode
from io import BytesIO
import base64

app = Flask(__name__)
app.secret_key = "farmer_app_secret_key_2026"

# MongoDB setup
MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/')
MONGO_DBNAME = os.environ.get('MONGO_DBNAME', 'farmer_app')
try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    client.admin.command('ping')  # Test connection
    db = client[MONGO_DBNAME]
    mongo_connected = True
    print(f"✅ Connected to MongoDB at {MONGO_URI}, using database '{MONGO_DBNAME}'")
except Exception as e:
    print(f"⚠️  MongoDB connection failed: {e}")
    print("⚠️  Please start MongoDB and restart the app")
    mongo_connected = False
    db = None

def get_db():
    """Get database connection"""
    if not mongo_connected or db is None:
        raise ConnectionError("MongoDB is not connected. Please start MongoDB server.")
    return db

def init_db():
    """Initialize MongoDB collections (no schema needed)"""
    db_conn = get_db()
    # Create collections and indexes
    if 'users' not in db_conn.list_collection_names():
        db_conn.create_collection('users')
        db_conn.users.create_index('email', unique=True)
    if 'products' not in db_conn.list_collection_names():
        db_conn.create_collection('products')
    if 'cart' not in db_conn.list_collection_names():
        db_conn.create_collection('cart')
    if 'orders' not in db_conn.list_collection_names():
        db_conn.create_collection('orders')
    if 'order_items' not in db_conn.list_collection_names():
        db_conn.create_collection('order_items')


def attach_farmer_info(product, db_conn):
    farmer = None
    farmer_id = product.get('farmer_id')
    if farmer_id is not None:
        try:
            if isinstance(farmer_id, str):
                farmer = db_conn.users.find_one({'_id': ObjectId(farmer_id)})
            else:
                farmer = db_conn.users.find_one({'_id': farmer_id})
        except Exception:
            farmer = None

    if farmer:
        product['farmer_name'] = farmer.get('name', 'Unknown')
        product['farmer_phone'] = farmer.get('phone', '')
        product['farmer_address'] = farmer.get('address', '')
    else:
        product['farmer_name'] = 'Unknown'
        product['farmer_phone'] = ''
        product['farmer_address'] = ''
    return product

def seed_products():
    """Seed the database with a list of 30 vegetable products."""
    db_conn = get_db()
    count = db_conn.products.count_documents({})
    farmers = list(db_conn.users.find({'role': 'farmer'}, {'_id': 1}))

    products = [
        ("Carrot", 40.0, 120, "kg", "Vegetables", "Crunchy orange carrots, rich in beta-carotene and fiber.", "https://via.placeholder.com/400x250.png?text=Carrot"),
        ("Potato", 25.0, 200, "kg", "Vegetables", "Fresh potatoes for cooking, roasting, and frying.", "https://via.placeholder.com/400x250.png?text=Potato"),
        ("Tomato", 55.0, 150, "kg", "Vegetables", "Juicy red tomatoes perfect for salads, sauces, and curries.", "https://via.placeholder.com/400x250.png?text=Tomato"),
        ("Onion", 35.0, 180, "kg", "Vegetables", "Aromatic onions for soups, stir-fries, and everyday cooking.", "https://via.placeholder.com/400x250.png?text=Onion"),
        ("Cabbage", 30.0, 90, "kg", "Vegetables", "Crunchy cabbage for slaws, stir-fries, and cooked dishes.", "https://via.placeholder.com/400x250.png?text=Cabbage"),
        ("Spinach", 60.0, 70, "kg", "Vegetables", "Fresh green spinach leaves packed with iron and vitamins.", "https://via.placeholder.com/400x250.png?text=Spinach"),
        ("Broccoli", 120.0, 45, "kg", "Vegetables", "Tender broccoli florets for steaming and healthy meals.", "https://via.placeholder.com/400x250.png?text=Broccoli"),
        ("Cauliflower", 80.0, 55, "kg", "Vegetables", "White cauliflower heads, great for curries, roasting, and soups.", "https://via.placeholder.com/400x250.png?text=Cauliflower"),
        ("Bell Pepper", 95.0, 60, "kg", "Vegetables", "Colorful bell peppers that brighten salads and stir-fries.", "https://via.placeholder.com/400x250.png?text=Bell+Pepper"),
        ("Cucumber", 35.0, 100, "kg", "Vegetables", "Cool cucumbers for salads, raitas, and refreshing snacks.", "https://via.placeholder.com/400x250.png?text=Cucumber"),
        ("Eggplant", 75.0, 80, "kg", "Vegetables", "Fresh eggplant perfect for curries, grills, and roasted dishes.", "https://via.placeholder.com/400x250.png?text=Eggplant"),
        ("Zucchini", 90.0, 50, "kg", "Vegetables", "Green zucchini ready for sautéing, baking, and healthy meals.", "https://via.placeholder.com/400x250.png?text=Zucchini"),
        ("Lettuce", 65.0, 45, "kg", "Vegetables", "Crisp lettuce leaves ideal for salads and sandwiches.", "https://via.placeholder.com/400x250.png?text=Lettuce"),
        ("Radish", 28.0, 100, "kg", "Vegetables", "Spicy radishes for salads, pickles, and garnishes.", "https://via.placeholder.com/400x250.png?text=Radish"),
        ("Green Peas", 150.0, 40, "kg", "Vegetables", "Sweet green peas for curries, pulao, and snacks.", "https://via.placeholder.com/400x250.png?text=Green+Peas"),
        ("Sweet Corn", 130.0, 55, "kg", "Vegetables", "Tender sweet corn kernels for soups, salads, and grills.", "https://via.placeholder.com/400x250.png?text=Sweet+Corn"),
        ("Kale", 140.0, 35, "kg", "Vegetables", "Healthy kale leaves for smoothies, salads, and sautés.", "https://via.placeholder.com/400x250.png?text=Kale"),
        ("French Beans", 95.0, 65, "kg", "Vegetables", "Fresh French beans for stir-fries and healthy side dishes.", "https://via.placeholder.com/400x250.png?text=French+Beans"),
        ("Pumpkin", 45.0, 80, "kg", "Vegetables", "Sweet pumpkin chunks for soups, stews, and desserts.", "https://via.placeholder.com/400x250.png?text=Pumpkin"),
        ("Sweet Potato", 70.0, 70, "kg", "Vegetables", "Nutritious sweet potatoes for roasting and baking.", "https://via.placeholder.com/400x250.png?text=Sweet+Potato"),
        ("Beetroot", 55.0, 60, "kg", "Vegetables", "Earthy beetroot for salads, juices, and healthy recipes.", "https://via.placeholder.com/400x250.png?text=Beetroot"),
        ("Celery", 120.0, 40, "kg", "Vegetables", "Fresh celery stalks for soups, salads, and snacks.", "https://via.placeholder.com/400x250.png?text=Celery"),
        ("Asparagus", 275.0, 20, "kg", "Vegetables", "Premium asparagus for grilling, roasting, and fine dining.", "https://via.placeholder.com/400x250.png?text=Asparagus"),
        ("Garlic", 180.0, 30, "kg", "Vegetables", "Fragrant garlic bulbs for cooking, sauces, and seasoning.", "https://via.placeholder.com/400x250.png?text=Garlic"),
        ("Ginger", 160.0, 45, "kg", "Vegetables", "Fresh ginger root for curries, tea, and healthy recipes.", "https://via.placeholder.com/400x250.png?text=Ginger"),
        ("Bottle Gourd", 35.0, 90, "kg", "Vegetables", "Tender bottle gourd for curries, soups, and stews.", "https://via.placeholder.com/400x250.png?text=Bottle+Gourd"),
        ("Bitter Gourd", 60.0, 45, "kg", "Vegetables", "Bitter gourd pieces for healthy cooking and traditional dishes.", "https://via.placeholder.com/400x250.png?text=Bitter+Gourd"),
        ("Okra", 95.0, 55, "kg", "Vegetables", "Fresh okra pods for frying, curries, and stews.", "https://via.placeholder.com/400x250.png?text=Okra"),
        ("Fennel", 110.0, 30, "kg", "Vegetables", "Crisp fennel bulbs for salads, roasting, and aromatic cooking.", "https://via.placeholder.com/400x250.png?text=Fennel"),
        ("Swiss Chard", 130.0, 30, "kg", "Vegetables", "Leafy Swiss chard great for sautés and healthy bowls.", "https://via.placeholder.com/400x250.png?text=Swiss+Chard")
    ]

    if count == 0:
        if not farmers:
            farmers = [{'_id': 1}]

        for index, (name, price, quantity, unit, category, description, image) in enumerate(products):
            farmer_id = farmers[index % len(farmers)]['_id']
            db_conn.products.insert_one({
                'farmer_id': farmer_id,
                'name': name,
                'price': price,
                'quantity': quantity,
                'unit': unit,
                'category': category,
                'description': description,
                'image': image,
                'created_at': datetime.now()
            })
    else:
        for i, farmer in enumerate(farmers):
            farmer_id = farmer['_id']
            farmer_count = db_conn.products.count_documents({'farmer_id': farmer_id})
            if farmer_count == 0:
                name, price, quantity, unit, category, description, image = products[i % len(products)]
                db_conn.products.insert_one({
                    'farmer_id': farmer_id,
                    'name': name,
                    'price': price,
                    'quantity': quantity,
                    'unit': unit,
                    'category': category,
                    'description': description,
                    'image': image,
                    'created_at': datetime.now()
                })

# Initialize database on startup
if mongo_connected:
    try:
        init_db()
        seed_products()
        print("✓ Database initialized successfully")
    except Exception as e:
        print(f"⚠️  Error initializing database: {e}")
else:
    print("⚠️  Skipping database initialization - MongoDB not connected")

# ==================== AUTHENTICATION ====================

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        role = request.form.get("role")
        phone = request.form.get("phone")
        address = request.form.get("address")
        
        if not all([name, email, password, role]):
            return "❌ All fields required", 400
        
        if password != confirm_password:
            return "❌ Passwords do not match", 400
        
        db_conn = get_db()
        
        if db_conn.users.find_one({'email': email}):
            return "❌ Email already registered", 400
        
        db_conn.users.insert_one({
            'name': name,
            'email': email,
            'password': generate_password_hash(password),
            'role': role,
            'phone': phone,
            'address': address,
            'created_at': datetime.now()
        })
        return redirect("/login?success=Registered successfully! Please login.")
    
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    success = request.args.get("success")
    
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        
        db_conn = get_db()
        user = db_conn.users.find_one({'email': email})
        
        if user and check_password_hash(user["password"], password):
            session["user_id"] = str(user["_id"])
            session["role"] = user["role"]
            session["name"] = user["name"]
            return redirect("/dashboard")
        
        return "❌ Invalid email or password", 401
    
    return render_template("login.html", success=success)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ==================== DASHBOARD ====================

@app.route("/")
def home():
    db_conn = get_db()
    query = request.args.get('q', '').strip()

    if query:
        products = list(db_conn.products.find({
            '$or': [
                {'name': {'$regex': query, '$options': 'i'}},
                {'category': {'$regex': query, '$options': 'i'}}
            ]
        }).sort("created_at", -1))
    else:
        products = list(db_conn.products.find().sort("created_at", -1))
    
    # Convert ObjectId and datetime to string for template
    for p in products:
        p['_id'] = str(p['_id'])
        p['farmer_id'] = str(p['farmer_id'])
        attach_farmer_info(p, db_conn)
        if 'created_at' in p and p['created_at']:
            p['created_at'] = p['created_at'].isoformat()
    
    return render_template("index.html", products=products)

@app.route("/product/<product_id>")
def view_product(product_id):
    db_conn = get_db()
    try:
        product = db_conn.products.find_one({'_id': ObjectId(product_id)})
    except Exception:
        product = None

    if not product:
        return "❌ Product not found", 404

    product['_id'] = str(product['_id'])
    product['farmer_id'] = str(product['farmer_id'])
    attach_farmer_info(product, db_conn)
    if 'created_at' in product and product['created_at']:
        product['created_at'] = product['created_at'].isoformat()

    return render_template("product_detail.html", product=product)

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/login")
    
    db_conn = get_db()
    user_id = ObjectId(session["user_id"])
    user = db_conn.users.find_one({'_id': user_id})
    
    if session["role"] == "farmer":
        products = list(db_conn.products.find({'farmer_id': user_id}).sort("created_at", -1))
        user_id_str = str(user_id)
        
        # Get ALL vegetables for the "Complete Inventory" section
        all_products = list(db_conn.products.find().sort("name", 1))
        
        # Get orders for products from this farmer
        product_ids = [p['_id'] for p in products]
        order_items = list(db_conn.order_items.find({'product_id': {'$in': product_ids}}))
        order_ids = [oi['order_id'] for oi in order_items]
        
        orders = list(db_conn.orders.find({'_id': {'$in': order_ids}}).sort("created_at", -1))
        
        # Convert orders to template-ready format
        for order in orders:
            customer = db_conn.users.find_one({'_id': order['customer_id']})
            if customer:
                order['customer_name'] = customer.get('name', '')
                order['customer_email'] = customer.get('email', '')
                order['customer_phone'] = customer.get('phone', '')
                order['customer_address'] = customer.get('address', '')
            order['_id'] = str(order['_id'])
            order['customer_id'] = str(order['customer_id'])
            # Convert datetime to string
            if 'created_at' in order and order['created_at']:
                order['created_at'] = order['created_at'].isoformat()
        
        # Convert own products to template-ready format
        for p in products:
            p['_id'] = str(p['_id'])
            p['farmer_id'] = str(p['farmer_id'])
            # Convert datetime to string
            if 'created_at' in p and p['created_at']:
                p['created_at'] = p['created_at'].isoformat()
        
        # Convert all products to template-ready format
        for p in all_products:
            p['_id'] = str(p['_id'])
            farmer = db_conn.users.find_one({'_id': p.get('farmer_id')})
            p['farmer_name'] = farmer.get('name', 'Unknown') if farmer else 'Unknown'
            p['farmer_id'] = str(p['farmer_id'])
            p['is_owner'] = (p['farmer_id'] == user_id_str)
            # Convert datetime to string
            if 'created_at' in p and p['created_at']:
                p['created_at'] = p['created_at'].isoformat()
        
        total_orders = len(orders)
        pending_orders = len([o for o in orders if o.get('status') == 'pending'])
        accepted_orders = len([o for o in orders if o.get('status') == 'accepted'])
        
        return render_template("farmer_dashboard.html", user=user, products=products, all_products=all_products, orders=orders, total_orders=total_orders, pending_orders=pending_orders, accepted_orders=accepted_orders)
    else:
        orders = list(db_conn.orders.find({'customer_id': user_id}).sort("created_at", -1))
        for order in orders:
            order['_id'] = str(order['_id'])
            order['customer_id'] = str(order['customer_id'])
            # Convert datetime to string
            if 'created_at' in order and order['created_at']:
                order['created_at'] = order['created_at'].isoformat()
        
        products = list(db_conn.products.find().sort("created_at", -1))
        for p in products:
            p['_id'] = str(p['_id'])
            p['farmer_id'] = str(p['farmer_id'])
            attach_farmer_info(p, db_conn)
            # Convert datetime to string
            if 'created_at' in p and p['created_at']:
                p['created_at'] = p['created_at'].isoformat()
        
        return render_template("customer_dashboard.html", user=user, orders=orders, products=products)

# ==================== PRODUCT MANAGEMENT ====================

@app.route("/add_product", methods=["GET", "POST"])
def add_product():
    if "user_id" not in session or session["role"] != "farmer":
        return redirect("/login")
    
    if request.method == "POST":
        name = request.form.get("name")
        price = float(request.form.get("price"))
        quantity = float(request.form.get("quantity"))
        unit = request.form.get("unit", "kg")
        category = request.form.get("category", "Vegetables")
        description = request.form.get("description", "")
        image = request.form.get("image", "default.jpg")
        
        if not name:
            return "❌ Product name is required", 400
        if price <= 0:
            return "❌ Price must be greater than 0", 400
        if quantity < 0:
            return "❌ Quantity cannot be negative", 400
        
        db_conn = get_db()
        db_conn.products.insert_one({
            'farmer_id': ObjectId(session["user_id"]),
            'name': name,
            'price': price,
            'quantity': quantity,
            'unit': unit,
            'category': category,
            'description': description,
            'image': image,
            'created_at': datetime.now()
        })
        return redirect("/dashboard")
    
    return render_template("add_product.html")

@app.route("/edit_product/<product_id>", methods=["GET", "POST"])
def edit_product(product_id):
    if "user_id" not in session or session["role"] != "farmer":
        return redirect("/login")
    
    db_conn = get_db()
    product = db_conn.products.find_one({'_id': ObjectId(product_id)})
    
    if not product:
        return "❌ Product not found", 404
    
    # Get farmer details for the product
    farmer = db_conn.users.find_one({'_id': product["farmer_id"]})
    farmer_name = farmer.get('name', 'Unknown') if farmer else 'Unknown'
    
    # Check ownership - convert both to strings for comparison
    product_farmer_id = str(product["farmer_id"])
    session_user_id = str(session["user_id"])
    is_owner = product_farmer_id == session_user_id
    
    if request.method == "POST":
        name = request.form.get("name")
        price = float(request.form.get("price"))
        quantity = float(request.form.get("quantity"))
        unit = request.form.get("unit", "kg")
        category = request.form.get("category", "Vegetables")
        description = request.form.get("description", "")
        image = request.form.get("image", product.get("image", "default.jpg"))
        
        if not name:
            return "❌ Product name is required", 400
        if price <= 0:
            return "❌ Price must be greater than 0", 400
        if quantity < 0:
            return "❌ Quantity cannot be negative", 400
        
        db_conn.products.update_one(
            {'_id': ObjectId(product_id)},
            {'$set': {
                'name': name,
                'price': price,
                'quantity': quantity,
                'unit': unit,
                'category': category,
                'description': description,
                'image': image,
                'updated_at': datetime.now()
            }}
        )
        return redirect("/dashboard")
    
    product['_id'] = str(product['_id'])
    product['farmer_id'] = product_farmer_id
    product['farmer_name'] = farmer_name
    product['is_owner'] = is_owner
    return render_template("edit_product.html", product=product)

@app.route("/delete_product/<product_id>", methods=["POST"])
def delete_product(product_id):
    if "user_id" not in session or session["role"] != "farmer":
        return redirect("/login")
    
    db_conn = get_db()
    product = db_conn.products.find_one({'_id': ObjectId(product_id)})
    
    if not product or str(product["farmer_id"]) != session["user_id"]:
        return "❌ Unauthorized", 403
    
    db_conn.products.delete_one({'_id': ObjectId(product_id)})
    # If request is AJAX, return JSON for client-side handling
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': True})
    return redirect("/dashboard")

# ==================== SHOPPING CART ====================

@app.route("/cart")
def view_cart():
    if "user_id" not in session:
        return redirect("/login")
    
    db_conn = get_db()
    user_id = ObjectId(session["user_id"])
    cart_items = list(db_conn.cart.find({'customer_id': user_id}))
    
    # Get product details for each cart item
    for item in cart_items:
        product = db_conn.products.find_one({'_id': item['product_id']})
        if product:
            item['name'] = product.get('name', '')
            item['price'] = product.get('price', 0)
        item['_id'] = str(item['_id'])
        item['customer_id'] = str(item['customer_id'])
        item['product_id'] = str(item['product_id'])
        if 'added_at' in item and item['added_at']:
            item['added_at'] = item['added_at'].isoformat()
    
    total = sum(item["quantity"] * item["price"] for item in cart_items)
    
    return render_template("cart.html", cart_items=cart_items, total=total)

@app.route("/add_to_cart/<product_id>", methods=["POST"])
def add_to_cart(product_id):
    if "user_id" not in session:
        return redirect("/login")
    
    quantity = float(request.form.get("quantity", 1))
    
    db_conn = get_db()
    product = db_conn.products.find_one({'_id': ObjectId(product_id)})
    
    if not product or quantity > product["quantity"]:
        return "❌ Insufficient stock", 400
    
    db_conn.cart.insert_one({
        'customer_id': ObjectId(session["user_id"]),
        'product_id': ObjectId(product_id),
        'quantity': quantity,
        'added_at': datetime.now()
    })
    
    if session.get("role") == "customer":
        return redirect("/dashboard")
    return redirect("/cart")

@app.route("/remove_from_cart/<cart_id>", methods=["POST"])
def remove_from_cart(cart_id):
    db_conn = get_db()
    db_conn.cart.delete_one({'_id': ObjectId(cart_id)})
    return redirect("/cart")

@app.route("/order/<order_id>")
def view_order(order_id):
    if "user_id" not in session or session["role"] != "farmer":
        return redirect("/login")
    
    db_conn = get_db()
    order = db_conn.orders.find_one({'_id': ObjectId(order_id)})
    
    if not order:
        return "Order not found", 404
    
    customer = db_conn.users.find_one({'_id': order['customer_id']})
    if customer:
        order['customer_name'] = customer.get('name', '')
        order['customer_email'] = customer.get('email', '')
        order['customer_phone'] = customer.get('phone', '')
        order['customer_address'] = customer.get('address', '')
    
    items = list(db_conn.order_items.find({'order_id': ObjectId(order_id)}))
    
    order['_id'] = str(order['_id'])
    order['customer_id'] = str(order['customer_id'])
    if 'created_at' in order and order['created_at']:
        if isinstance(order['created_at'], datetime):
            order['created_at'] = order['created_at'].isoformat()
    if 'delivery_date' in order and isinstance(order['delivery_date'], datetime):
        order['delivery_date'] = order['delivery_date'].strftime('%Y-%m-%d')
    for item in items:
        item['_id'] = str(item['_id'])
        item['order_id'] = str(item['order_id'])
        item['product_id'] = str(item['product_id'])
    
    return render_template("order_details.html", order=order, items=items)

@app.route("/update_order_status/<order_id>", methods=["POST"])
def update_order_status(order_id):
    if "user_id" not in session or session["role"] != "farmer":
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    
    status = request.form.get("status") or (request.json.get("status") if request.is_json else request.form.get("status"))
    if status not in ["pending", "accepted", "rejected", "delivered"]:
        return jsonify({"success": False, "message": "Invalid status"}), 400
    
    db_conn = get_db()
    db_conn.orders.update_one(
        {'_id': ObjectId(order_id)},
        {'$set': {'status': status}}
    )
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({"success": True, "status": status})
    return redirect("/dashboard")

# ==================== ORDERS ====================

@app.route("/checkout", methods=["POST"])
def checkout():
    if "user_id" not in session:
        return redirect("/login")
    
    db_conn = get_db()
    customer_id = ObjectId(session["user_id"])
    
    cart_items = list(db_conn.cart.find({'customer_id': customer_id}))
    
    if not cart_items:
        return "❌ Cart is empty", 400
    
    total_price = 0
    order_items_data = []
    
    for item in cart_items:
        product = db_conn.products.find_one({'_id': item['product_id']})
        if not product:
            continue
        total = item["quantity"] * product["price"]
        total_price += total
        order_items_data.append({
            'product_id': item['product_id'],
            'product_name': product['name'],
            'quantity': item['quantity'],
            'price': product['price'],
            'farmer_id': product['farmer_id']
        })
    
    payment_method = request.form.get("payment_method", "cash")
    
    # Create order
    order_doc = db_conn.orders.insert_one({
        'customer_id': customer_id,
        'total_price': total_price,
        'payment_method': payment_method,
        'status': 'pending',
        'delivery_date': '24-48 hours',
        'created_at': datetime.now()
    })
    order_id = order_doc.inserted_id
    
    # Add items to order and reduce stock
    for item_data in order_items_data:
        db_conn.order_items.insert_one({
            'order_id': order_id,
            'product_id': item_data['product_id'],
            'product_name': item_data['product_name'],
            'quantity': item_data['quantity'],
            'price': item_data['price'],
            'farmer_id': item_data['farmer_id']
        })
        
        # Reduce stock
        db_conn.products.update_one(
            {'_id': item_data['product_id']},
            {'$inc': {'quantity': -item_data['quantity']}}
        )
    
    # Clear cart
    db_conn.cart.delete_many({'customer_id': customer_id})
    
    # Route to UPI payment page if UPI is selected
    if payment_method == "upi":
        return redirect(f"/upi_payment/{order_id}")
    
    return redirect(f"/order_confirmation/{order_id}")

@app.route("/upi_payment/<order_id>")
def upi_payment(order_id):
    """Display UPI payment page with QR code"""
    if "user_id" not in session:
        return redirect("/login")
    
    db_conn = get_db()
    order = db_conn.orders.find_one({'_id': ObjectId(order_id)})
    
    if not order:
        return "❌ Order not found", 404
    
    # Get user info
    user = db_conn.users.find_one({'_id': ObjectId(session['user_id'])})
    
    # Generate UPI string for payment
    # Format: upi://pay?pa=UPI_ID&pn=MERCHANT_NAME&am=AMOUNT&tr=TRANSACTION_ID
    upi_id = "merchant@upi"  # This should be configurable
    merchant_name = "Farmer App"
    amount = order['total_price']
    transaction_id = str(order['_id'])
    
    upi_string = f"upi://pay?pa={upi_id}&pn={merchant_name}&am={amount}&tr={transaction_id}"
    
    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(upi_string)
    qr.make(fit=True)
    
    # Convert QR code to image
    qr_img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert image to base64 for embedding in HTML
    buffer = BytesIO()
    qr_img.save(buffer, format='PNG')
    buffer.seek(0)
    qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()
    
    order['_id'] = str(order['_id'])
    
    return render_template(
        "upi_payment.html", 
        order=order,
        qr_code=qr_code_base64,
        upi_id=upi_id,
        amount=amount
    )

@app.route("/confirm_upi_payment/<order_id>", methods=["POST"])
def confirm_upi_payment(order_id):
    """Confirm UPI payment and mark order as paid"""
    if "user_id" not in session:
        return redirect("/login")
    
    db_conn = get_db()
    
    # Update order status to confirmed
    db_conn.orders.update_one(
        {'_id': ObjectId(order_id)},
        {'$set': {'status': 'confirmed', 'payment_confirmed_at': datetime.now()}}
    )
    
    return redirect(f"/order_confirmation/{order_id}")

@app.route("/order_confirmation/<order_id>")
def order_confirmation(order_id):
    db_conn = get_db()
    order = db_conn.orders.find_one({'_id': ObjectId(order_id)})
    items = list(db_conn.order_items.find({'order_id': ObjectId(order_id)}))
    
    for item in items:
        item['_id'] = str(item['_id'])
        item['order_id'] = str(item['order_id'])
        item['product_id'] = str(item['product_id'])
        item['farmer_id'] = str(item['farmer_id'])
    
    order['_id'] = str(order['_id'])
    order['customer_id'] = str(order['customer_id'])
    if 'created_at' in order and order['created_at']:
        order['created_at'] = order['created_at'].isoformat()
    
    return render_template("order_confirmation.html", order=order, items=items)

@app.route("/my_orders")
def my_orders():
    if "user_id" not in session:
        return redirect("/login")
    
    db_conn = get_db()
    user_id = ObjectId(session["user_id"])
    
    if session["role"] == "customer":
        orders = list(db_conn.orders.find({'customer_id': user_id}).sort("created_at", -1))
    else:
        # Farmer view - get orders containing their products
        order_items = list(db_conn.order_items.find({'farmer_id': user_id}))
        order_ids = [oi['order_id'] for oi in order_items]
        orders = list(db_conn.orders.find({'_id': {'$in': order_ids}}).sort("created_at", -1))
    
    for order in orders:
        order['_id'] = str(order['_id'])
        order['customer_id'] = str(order['customer_id'])
        if 'created_at' in order and order['created_at']:
            order['created_at'] = order['created_at'].isoformat()
    
    return render_template("my_orders.html", orders=orders)

@app.route("/api/products")
def api_products():
    db_conn = get_db()
    products = list(db_conn.products.find())
    
    for p in products:
        p['_id'] = str(p['_id'])
        p['farmer_id'] = str(p['farmer_id'])
    
    return jsonify(products)

if __name__ == "__main__":
    app.run(debug=True)
