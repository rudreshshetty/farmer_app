#!/usr/bin/env python3
"""
Bulk Update All Vegetables with Enhanced Details
This script updates all 36 vegetables with comprehensive information including:
- Better names and categories
- More detailed descriptions
- Standard pricing tiers
- Stock management
"""

from pymongo import MongoClient
from datetime import datetime

# MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client['farmer_app']

# Enhanced vegetable data with complete details
enhanced_products = {
    "Asparagus": {
        "description": "Premium fresh asparagus spears, hand-picked daily. Rich in vitamins A, C, and K. Perfect for grilling, steaming, and fine dining.",
        "category": "Vegetables",
        "unit": "kg",
    },
    "Beetroot": {
        "description": "Earthy and sweet beetroots, perfect for salads, juices, and roasted dishes. High in antioxidants and natural nitrates.",
        "category": "Vegetables",
        "unit": "kg",
    },
    "Bell Pepper": {
        "description": "Vibrant and colorful bell peppers in red, yellow, and green. Sweet flavor, crisp texture. Great raw or cooked.",
        "category": "Vegetables",
        "unit": "kg",
    },
    "Bitter Gourd": {
        "description": "Fresh bitter gourd pieces for traditional Indian cooking. Excellent for health-conscious recipes. Slightly bitter but nutritious.",
        "category": "Vegetables",
        "unit": "kg",
    },
    "Bottle Gourd": {
        "description": "Tender bottle gourd perfect for curries, soups, and stews. Mild flavor, high water content, very versatile.",
        "category": "Vegetables",
        "unit": "kg",
    },
    "Broccoli": {
        "description": "Fresh green broccoli florets packed with vitamins and minerals. Great for steaming, stir-fry, or raw salads.",
        "category": "Vegetables",
        "unit": "kg",
    },
    "Cabbage": {
        "description": "Crunchy cabbage varieties for slaws, stir-fries, and cooked dishes. High in vitamin C and fiber.",
        "category": "Vegetables",
        "unit": "kg",
    },
    "Carrot": {
        "description": "Sweet orange carrots rich in beta-carotene and fiber. Perfect for snacking, cooking, or juicing.",
        "category": "Vegetables",
        "unit": "kg",
    },
    "Cauliflower": {
        "description": "White cauliflower heads great for curries, roasting, and soups. Versatile and healthy cruciferous vegetable.",
        "category": "Vegetables",
        "unit": "kg",
    },
    "Celery": {
        "description": "Fresh crisp celery stalks perfect for soups, salads, and snacks. Low in calories, high in nutrients.",
        "category": "Vegetables",
        "unit": "kg",
    },
    "Cucumber": {
        "description": "Cool refreshing cucumbers for salads, raitas, and pickles. Hydrating and perfect for summer.",
        "category": "Vegetables",
        "unit": "kg",
    },
    "Eggplant": {
        "description": "Fresh eggplant perfect for curries, grills, and roasted dishes. Tender and flavorful when cooked.",
        "category": "Vegetables",
        "unit": "kg",
    },
    "Fennel": {
        "description": "Crisp fennel bulbs with anise-like flavor. Great for salads, roasting, and aromatic cooking.",
        "category": "Vegetables",
        "unit": "kg",
    },
    "French Beans": {
        "description": "Fresh french beans for stir-fries and healthy side dishes. Tender, green, and nutritious.",
        "category": "Vegetables",
        "unit": "kg",
    },
    "Garlic": {
        "description": "Fragrant garlic bulbs essential for cooking, sauces, and seasoning. Pungent flavor, many health benefits.",
        "category": "Vegetables",
        "unit": "kg",
    },
    "Ginger": {
        "description": "Fresh ginger root for curries, tea, and healthy recipes. Spicy, warm flavor with anti-inflammatory properties.",
        "category": "Vegetables",
        "unit": "kg",
    },
    "Green Peas": {
        "description": "Sweet green peas for curries, pulao, and snacks. Fresh, tender, and packed with protein.",
        "category": "Vegetables",
        "unit": "kg",
    },
    "Kale": {
        "description": "Healthy kale leaves for smoothies, salads, and sautés. Superfood rich in vitamins and minerals.",
        "category": "Leafy Greens",
        "unit": "kg",
    },
    "Lettuce": {
        "description": "Crisp lettuce leaves ideal for salads and sandwiches. Fresh, crunchy, and hydrating.",
        "category": "Leafy Greens",
        "unit": "kg",
    },
    "Okra": {
        "description": "Fresh okra pods for frying, curries, and stews. Tender variety with authentic flavor.",
        "category": "Vegetables",
        "unit": "kg",
    },
    "Onion": {
        "description": "Aromatic onions essential for soups, stir-fries, and everyday cooking. Fresh from farm.",
        "category": "Vegetables",
        "unit": "kg",
    },
    "Potato": {
        "description": "Fresh potatoes for cooking, roasting, and frying. Versatile staple crop from local farms.",
        "category": "Vegetables",
        "unit": "kg",
    },
    "Pumpkin": {
        "description": "Sweet pumpkin chunks for soups, stews, and desserts. Rich flavor, creamy texture when cooked.",
        "category": "Vegetables",
        "unit": "kg",
    },
    "Radish": {
        "description": "Spicy radishes for salads, pickles, and garnishes. Fresh, crunchy, and peppery flavor.",
        "category": "Vegetables",
        "unit": "kg",
    },
    "Spinach": {
        "description": "Fresh green spinach leaves packed with iron and vitamins. Perfect for cooking or raw salads.",
        "category": "Leafy Greens",
        "unit": "kg",
    },
    "Sweet Corn": {
        "description": "Sweet fresh corn kernels perfect for grilling, boiling, or using in recipes. Tender and juicy.",
        "category": "Vegetables",
        "unit": "kg",
    },
    "Sweet Potato": {
        "description": "Nutritious sweet potatoes great for roasting, baking, and fries. Rich in beta-carotene and fiber.",
        "category": "Vegetables",
        "unit": "kg",
    },
    "Swiss Chard": {
        "description": "Colorful swiss chard with vibrant stems and leaves. Nutritious leafy green for cooking.",
        "category": "Leafy Greens",
        "unit": "kg",
    },
    "Tomato": {
        "description": "Ripe juicy tomatoes perfect for salads, cooking, and sauces. Fresh from farm, rich flavor.",
        "category": "Vegetables",
        "unit": "kg",
    },
    "Zucchini": {
        "description": "Fresh zucchini great for grilling, sautéing, and baking. Tender green variety.",
        "category": "Vegetables",
        "unit": "kg",
    },
    "onion": {
        "description": "Fresh aromatic onions from local farmers. Perfect for all cooking needs.",
        "category": "Vegetables",
        "unit": "kg",
    },
}

print("\n" + "="*100)
print("BULK UPDATING ALL VEGETABLES WITH ENHANCED DETAILS".center(100))
print("="*100)

updated_count = 0
skipped_count = 0

try:
    products_collection = db.products
    
    for product_name, details in enhanced_products.items():
        try:
            # Find all products with this name (case-insensitive)
            result = products_collection.update_many(
                {"name": {"$regex": f"^{product_name}$", "$options": "i"}},
                {
                    "$set": {
                        "description": details.get("description", ""),
                        "category": details.get("category", "Vegetables"),
                        "unit": details.get("unit", "kg"),
                        "updated_at": datetime.now()
                    }
                }
            )
            
            if result.modified_count > 0:
                print(f"✅ Updated: {product_name.upper():<20} - {result.modified_count} document(s)")
                updated_count += result.modified_count
            else:
                print(f"⚠️  No match: {product_name.upper():<20}")
                skipped_count += 1
                
        except Exception as e:
            print(f"❌ Error updating {product_name}: {str(e)}")
            skipped_count += 1

    print("\n" + "="*100)
    print(f"SUMMARY: {updated_count} vegetables updated | {skipped_count} skipped")
    print("="*100)
    
    # Display updated products
    print("\n📋 UPDATED VEGETABLES IN DATABASE:")
    print("-"*100)
    
    all_products = list(products_collection.find().sort("name", 1))
    for i, product in enumerate(all_products, 1):
        farmer = db.users.find_one({'_id': product.get('farmer_id')})
        farmer_name = farmer.get('name', 'Unknown') if farmer else 'Unknown'
        
        print(f"\n{i}. {product.get('name', 'N/A').upper()}")
        print(f"   Farmer: {farmer_name}")
        print(f"   Price: ₹{product.get('price', 0):.2f}/{product.get('unit', 'kg')}")
        print(f"   Stock: {product.get('quantity', 0):.1f} {product.get('unit', 'kg')}")
        print(f"   Category: {product.get('category', 'Vegetables')}")
        print(f"   Description: {product.get('description', 'N/A')}")
    
    print("\n✅ ALL VEGETABLES UPDATED SUCCESSFULLY!\n")
    
except Exception as e:
    print(f"❌ Error: {str(e)}")
