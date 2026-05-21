import sqlite3

conn = sqlite3.connect('farmer_app.db')
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# Get all products
cur.execute('''SELECT p.*, u.name as farmer_name 
               FROM products p 
               LEFT JOIN users u ON p.farmer_id = u.id 
               ORDER BY p.name''')
products = cur.fetchall()

print('\n' + '='*140)
print('ALL VEGETABLES IN DATABASE'.center(140))
print('='*140 + '\n')
print(f'Total Products: {len(products)}\n')

# Calculate total inventory value
total_value = sum(p['price'] * p['quantity'] for p in products)
total_stock = sum(p['quantity'] for p in products)

for i, p in enumerate(products, 1):
    farmer_name = p['farmer_name'] if p['farmer_name'] else 'Unknown Farmer'
    print(f'{i}. {p["name"].upper()}')
    print(f'   Price: ₹{p["price"]:.2f} per {p["unit"]}')
    print(f'   Available Stock: {p["quantity"]:.1f} {p["unit"]}')
    print(f'   Stock Value: ₹{p["price"] * p["quantity"]:.2f}')
    print(f'   Category: {p["category"]}')
    print(f'   Farmer: {farmer_name}')
    print(f'   Description: {p["description"]}')
    print(f'   Image: {p["image"]}')
    print()

print('='*140)
print(f'\nSUMMARY:')
print(f'Total Products: {len(products)}')
print(f'Total Stock: {total_stock:.1f} kg')
print(f'Total Inventory Value: ₹{total_value:.2f}')
print('='*140 + '\n')

conn.close()
