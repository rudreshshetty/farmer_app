import sqlite3

conn = sqlite3.connect('farmer_app.db')
cur = conn.cursor()
cur.execute("SELECT id FROM users WHERE email = 'rudreshshettyp@gmail.com' AND role = 'farmer'")
row = cur.fetchone()
if not row:
    raise SystemExit('Farmer user not found')
farmer_id = row[0]
cur.execute('UPDATE products SET farmer_id = ? WHERE farmer_id != ?', (farmer_id, farmer_id))
conn.commit()
print('Reassigned products to farmer_id', farmer_id)
cur.execute('SELECT farmer_id, COUNT(*) FROM products GROUP BY farmer_id')
print(cur.fetchall())
conn.close()
