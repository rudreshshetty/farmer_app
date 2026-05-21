# QUICK START

## ⚡ 5-Minute Setup

### 1️⃣ Start MongoDB
```powershell
Start-Process "C:\Program Files\MongoDB\Server\8.2\bin\mongod.exe"
# Wait 3 seconds
```

### 2️⃣ Migrate Data
```bash
cd c:\Users\LENOVO\Downloads\farmer_app\farmer_app
uv run python migrate_to_mongodb.py
```

### 3️⃣ Run App
```bash
uv run python app.py
```

### 4️⃣ Open Browser
```
http://127.0.0.1:5000
```

---

## 💡 Test Order Visibility

### 👥 Accounts to Use

**FARMER #1 - Rudresh** (has 32 products)
```
Email: rudreshshettyp@gmail.com
```

**FARMER #2 - Ram** (has 1 product)
```
Email: likhi295@gmail.com
```

**CUSTOMER** (ready to order)
```
Email: test_customer@example.com
Password: password
```

### 📝 Test Steps

1. **Login as CUSTOMER** (test_customer@example.com / password)
2. **Browse Products** → Add Tomato (from Rudresh) + Onion (from Ram) to cart
3. **Checkout**
4. **View "My Orders"** → See your order ✓
5. **Logout**
6. **Login as RUDRESH** (rudreshshettyp@gmail.com)
7. **Go to Dashboard** → See "Incoming Orders" ← **ORDER APPEARS HERE!** ✓
8. **Click "View Order"** → See customer details
9. **Click "Accept Order"** → Status changes ✓
10. **Logout**
11. **Login as RAM** (likhi295@gmail.com)
12. **Go to Dashboard** → **SAME ORDER APPEARS HERE TOO!** ✓
    (But only shows items that Ram sells)

---

## 🎯 What You'll See

### Customer View (My Orders):
```
Order #XYZ
├─ Tomato (5 kg) from Rudresh
├─ Onion (3 kg) from Ram
└─ Total: ₹500 | Status: Pending
```

### Farmer #1 View (Rudresh's Dashboard):
```
Incoming Orders
├─ Order #XYZ | Status: Pending
│  ├─ Customer: Test Customer
│  ├─ Phone: +91...
│  ├─ Items: Tomato (5 kg)
│  └─ [Accept] [Reject]
```

### Farmer #2 View (Ram's Dashboard):
```
Incoming Orders  
├─ Order #XYZ | Status: Pending
│  ├─ Customer: Test Customer
│  ├─ Phone: +91...
│  ├─ Items: Onion (3 kg)
│  └─ [Accept] [Reject]
```

---

## ✨ Key Feature: Order Visibility

**The Magic:**
- When customer orders from Rudresh's products → Rudresh sees it
- When customer orders from Ram's products → Ram sees it
- When customer orders from BOTH → Both see the SAME order
- Each farmer can independently update their items status

**How it works:**
- `order_items` collection stores `farmer_id`
- Farmer dashboard queries: `order_items where farmer_id = me`
- Shows all orders containing that farmer's products

---

## 📊 Database Check

Open **MongoDB Compass:**
```
Connection: mongodb://localhost:27017
Database: farmer_app
Collections:
  - users (8 docs)
  - products (35 docs)
  - orders (0-N docs, grows as you order)
  - order_items (0-N docs)
  - cart (0-N docs)
```

---

## 🐛 Debug Commands

### See all farmers
```bash
uv run python -c "
from pymongo import MongoClient
client = MongoClient('mongodb://localhost:27017/')
db = client['farmer_app']
farmers = db.users.find({'role': 'farmer'})
for f in farmers:
    print(f['name'], f['email'])
"
```

### See orders for a farmer
```bash
# First get farmer's ObjectId from MongoDB Compass
# Then:
uv run python -c "
from pymongo import MongoClient
from bson import ObjectId
client = MongoClient('mongodb://localhost:27017/')
db = client['farmer_app']
# Replace with actual ObjectId
order_items = db.order_items.find({'farmer_id': ObjectId('...')})
for item in order_items:
    print(item)
"
```

### Reset Everything
```bash
uv run python migrate_to_mongodb.py
# This clears and re-imports all SQLite data
```

---

## 📞 If Something Goes Wrong

### "MongoDB connection failed"
→ Start MongoDB: `Start-Process "C:\Program Files\MongoDB\Server\8.2\bin\mongod.exe"`

### "Collection not found"
→ Run migration: `uv run python migrate_to_mongodb.py`

### "Order not showing for farmer"
→ Check MongoDB Compass → Look in `order_items` → Verify `farmer_id` field has the farmer's ID

### "Can't see other farmer's orders"
→ This is CORRECT! Each farmer only sees their own orders. That's the feature!

---

## ✅ Task Complete!

Your requirement **"if customer orders, farmer should see it"** is now implemented!

The app is ready to use! 🚀
