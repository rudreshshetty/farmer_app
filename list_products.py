from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['farmer_app']

products = list(db.products.find().sort('name', 1))
print('\n' + '='*120)
print('ALL VEGETABLES IN DATABASE'.center(120))
print('='*120 + '\n')
print(f'Total Products: {len(products)}\n')

for i, p in enumerate(products, 1):
    print(f'{i}. NAME: {p.get("name", "N/A")}')
    print(f'   Price: ₹{p.get("price", 0):.2f} per {p.get("unit", "kg")}')
    print(f'   Available Stock: {p.get("quantity", 0)} {p.get("unit", "kg")}')
    print(f'   Category: {p.get("category", "N/A")}')
    print(f'   Description: {p.get("description", "N/A")}')
    print(f'   Image: {p.get("image", "N/A")}')
    print()

print('='*120)
print(f'\nTotal Value of Stock: ₹{sum(p.get("price", 0) * p.get("quantity", 0) for p in products):.2f}')
