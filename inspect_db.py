import sqlite3

conn = sqlite3.connect('farmer_app.db')
cur = conn.cursor()
print('user_count:', cur.execute('SELECT COUNT(*) FROM users').fetchone()[0])
print('farmer_rows:')
for row in cur.execute('SELECT id, name, email, role FROM users WHERE role = "farmer"'):
    print(row)
print('product_count:', cur.execute('SELECT COUNT(*) FROM products').fetchone()[0])
print('products_by_farmer:')
for row in cur.execute('SELECT farmer_id, COUNT(*) FROM products GROUP BY farmer_id'):
    print(row)
print('example_products:')
for row in cur.execute('SELECT id, farmer_id, name, price, quantity, unit, category FROM products ORDER BY id LIMIT 20'):
    print(row)
conn.close()
