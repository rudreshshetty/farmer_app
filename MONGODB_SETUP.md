# Farmer App - MongoDB Setup & Usage Guide

## 📋 Overview
This is a Flask-based Farmer-to-Customer marketplace app that uses **MongoDB** as the database instead of SQLite.

### Key Features
✓ Customer can browse & order vegetables  
✓ Farmer can manage products & see customer orders  
✓ Orders show for both buyer and seller  
✓ Real-time inventory management

---

## 🚀 Getting Started

### 1. **Install MongoDB**

#### Option A: Using Windows Package Manager (Recommended)
```powershell
winget install MongoDB.Server
winget install MongoDB.Compass.Full
```

#### Option B: Manual Installation
- Download from: https://www.mongodb.com/try/download/community
- Install to `C:\Program Files\MongoDB\`

---

### 2. **Start MongoDB Service**

#### On Windows:
```powershell
# Start MongoDB daemon
Start-Process "C:\Program Files\MongoDB\Server\8.2\bin\mongod.exe"

# Or create a service (run as admin)
"C:\Program Files\MongoDB\Server\8.2\bin\mongod.exe" --install --logpath "C:\mongodb\logs\mongo.log"
net start MongoDB
```

#### Verify it's running:
```powershell
# Test connection
curl http://localhost:27017/
```

---

### 3. **Migrate Data from SQLite to MongoDB**

```bash
cd c:\Users\LENOVO\Downloads\farmer_app\farmer_app
uv run python migrate_to_mongodb.py
```

**What this does:**
- Copies all users, products, orders from SQLite to MongoDB
- Creates proper indexes for performance
- Maps user IDs correctly

---

### 4. **Start the Flask App**

```bash
uv run python app.py
```

The app will start on: **http://127.0.0.1:5000**

---

## 👥 Test Accounts

### Farmer Accounts:
- **Email:** rudreshshettyp@gmail.com  
- **Password:** (use registration or check database)

- **Email:** test_farmer@example.com  
- **Password:** password

### Customer Accounts:
- **Email:** customer@test.com  
- **Password:** password

- **Email:** test_customer@example.com  
- **Password:** password

---

## 🎯 How Order Visibility Works

### Customer View:
1. Browse products from "Shop"
2. Add to cart
3. Click "Checkout"
4. Order appears in "My Orders" section

### Farmer View:
1. When a customer orders their products
2. Order automatically appears in "Farmer Dashboard" → "Incoming Orders"
3. Farmer can update order status (Pending → Accepted → Delivered)

**Database Logic:**
- Order Items store both `order_id` and `farmer_id`
- When farmer logs in, the app queries for orders containing their products
- Multiple farmers can see the same order if they supply different items

---

## 📊 MongoDB Collections Structure

```
farmer_app/
├── users
│   ├── _id (ObjectId)
│   ├── name, email, password
│   ├── role (farmer/customer)
│   └── phone, address
│
├── products
│   ├── _id (ObjectId)
│   ├── farmer_id (ref: users._id)
│   ├── name, price, quantity, unit
│   ├── category, description, image
│   └── created_at
│
├── orders
│   ├── _id (ObjectId)
│   ├── customer_id (ref: users._id)
│   ├── total_price, payment_method, status
│   └── created_at
│
├── order_items
│   ├── _id (ObjectId)
│   ├── order_id (ref: orders._id)
│   ├── product_id (ref: products._id)
│   ├── farmer_id (ref: users._id) ← KEY FOR FARMER VISIBILITY
│   ├── product_name, quantity, price
│   └── timestamp
│
└── cart
    ├── _id (ObjectId)
    ├── customer_id (ref: users._id)
    ├── product_id (ref: products._id)
    ├── quantity
    └── added_at
```

---

## 🔍 Verify Setup with MongoDB Compass

1. Open **MongoDB Compass**
2. Connection: `mongodb://localhost:27017`
3. Click "Connect"
4. Navigate to `farmer_app` database
5. Explore collections

---

## 📝 Available Scripts

| Script | Purpose |
|--------|---------|
| `app.py` | Main Flask application |
| `migrate_to_mongodb.py` | Migrate SQLite → MongoDB |
| `display_all_products.py` | List all vegetables |
| `inspect_db.py` | View SQLite database stats |

---

## ⚠️ Troubleshooting

### MongoDB Connection Failed
```
Error: MongoDB connection failed
Solution: Start MongoDB service or check if port 27017 is open
```

### Database Not Found After Restart
```
Solution: Run migration script again: 
uv run python migrate_to_mongodb.py
```

### Order Not Showing for Farmer
```
Check: order_items collection has the farmer_id field
Query: db.order_items.find({farmer_id: ObjectId("...")})
```

---

## 🔐 Database Connection String

**Development (Local):**
```
mongodb://localhost:27017/farmer_app
```

**Production (if using Atlas):**
```
mongodb+srv://username:password@cluster.mongodb.net/farmer_app?retryWrites=true&w=majority
```

Update in `app.py` line ~12:
```python
client = MongoClient('mongodb://YOUR_CONNECTION_STRING')
```

---

## 📊 Sample Queries

### Find all orders for a farmer:
```javascript
db.order_items.find({farmer_id: ObjectId("...")}).distinct("order_id")
```

### Get order details with customer info:
```javascript
db.orders.aggregate([
  {$match: {_id: ObjectId("...")}},
  {$lookup: {
    from: "users",
    localField: "customer_id",
    foreignField: "_id",
    as: "customer"
  }}
])
```

### Check farmer's products:
```javascript
db.products.find({farmer_id: ObjectId("...")})
```

---

## 🎓 Next Steps

1. ✓ Set up MongoDB
2. ✓ Migrate data
3. ✓ Start the app
4. ✓ Test customer ordering
5. ✓ Verify farmer sees order
6. 🔄 Update order status as farmer

---

## 📞 Support

For issues or questions:
- Check MongoDB logs: `C:\mongodb\logs\mongo.log`
- Run Flask in debug mode for detailed errors
- Use MongoDB Compass to inspect data

