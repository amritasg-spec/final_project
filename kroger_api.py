import base64
import requests

CLIENT_ID = "groceryfinalproject-bbc9kr33"
CLIENT_SECRET = "JUn9T6lrU1-dwEc8PMRhatWssGOuZYLAzLqLIaeT"

# Look up this list to convert string category names to integer and vice versa
categories = [
    "Unknown",
    "Adult Beverage",
    "Bakery",
    "Baking Goods",
    "Beverages",
    "Breakfast",
    "Canned & Packaged",
    "Cleaning Products",
    "Condiment & Sauces",
    "Dairy",
    "Deli",
    "Frozen",
    "International",
    "Kitchen",
    "Meat & Seafood",
    "Natural & Organic",
    "Pasta, Sauces, Grain",
    "Produce",
    "Snacks",
]

def encode_categories(input_categories):
    """
    Convert a list of category strings into integer IDs.
    Unknown categories map to index 0 ("Unknown").
    Duplicates are removed and the final list is sorted by ID.
    """
    # Build lookup table from the global master list
    mapping = {cat: i for i, cat in enumerate(categories)}

    unique_ids = set()

    for cat in input_categories:
        if cat in mapping:
            unique_ids.add(mapping[cat])
        else:
            print(f"[encode_categories] Warning: category '{cat}' not found. Using ID 0.")
            unique_ids.add(0)

    return sorted(unique_ids)

# Look up this list to convert string fulfillments to integer and vice versa
fulfillment_types = [
    "unknown",
    "curbside",
    "delivery",
    "inStore",
    "shipToHome"
]

def encode_fulfillments(input_fulfillments):
    """
    Convert a dict of fulfillment flags into integer IDs.
    Only fulfillments with truthy values are included.
    Unknown fulfillments map to index 0 ("unknown").
    Duplicates are removed and the final list is sorted by ID.
    """
    mapping = {ful: i for i, ful in enumerate(fulfillment_types)}
    unique_ids = set()
    for ful, enabled in input_fulfillments.items():
        if enabled:
            if ful in mapping:
                unique_ids.add(mapping[ful])
            else:
                print(f"[encode_fulfillments] Warning: fulfillment '{ful}' not found. Using ID 0.")
                unique_ids.add(0)
    return sorted(unique_ids)

def get_access_token():
    token_url = "https://api.kroger.com/v1/connect/oauth2/token"
    
    auth_string = f"{CLIENT_ID}:{CLIENT_SECRET}"
    b64_auth = base64.b64encode(auth_string.encode()).decode()

    headers = {
        "Authorization": f"Basic {b64_auth}",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    data = {
        "grant_type": "client_credentials",
        "scope": "product.compact"
    }

    response = requests.post(token_url, headers=headers, data=data)
    response.raise_for_status()
    return response.json()["access_token"]

def get_kroger_products_json(query):
    token = get_access_token()

    url = "https://api.kroger.com/v1/products"

    headers = {
        "Authorization": f"Bearer {token}"
    }

    params = {
        "filter.term": query,
        "filter.limit": 5,
        "filter.locationId": "01400376"
    }

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()

def process_kroger_result_json(data):
    products = data.get("data", [])
    result = []

    for p in products:
        item = p["items"][0]  # Assumption: every product has one item

        # Convert categories into a comma-separated list of IDs
        encoded_categories = encode_categories(p.get("categories", []))
        categories = ", ".join(str(n) for n in encoded_categories)

        # Price fields
        price_obj = item.get("price", {})
        regular_price = price_obj.get("regular")
        promo_price = price_obj.get("promo")

        # Stock
        stock_level = item.get("inventory", {}).get("stockLevel")

        # Fulfillment: make comma-separated list of properties that are True
        fulfillment = item.get("fulfillment", {})
        encoded_fulfillments = encode_fulfillments(fulfillment)
        fulfillment_str = ", ".join(str(n) for n in encoded_fulfillments)

        result.append({
            "productId": int(p.get("productId")),
            "brand": p.get("brand"),
            "description": p.get("description"),
            "categories": categories,
            "regularPrice": regular_price,
            "promoPrice": promo_price,
            "stockLevel": stock_level,
            "fulfillment": fulfillment_str
        })

    return result

def create_grocery_table(cur):
    # Create table if it doesn't exist
    cur.execute("""
        CREATE TABLE IF NOT EXISTS grocery_products (
            product_id INTEGER PRIMARY KEY,
            ingredient_name TEXT,
            brand TEXT,
            description TEXT,
            categories TEXT,
            regular_price REAL,
            promo_price REAL,
            stock_level TEXT,
            fulfillment TEXT
        );
    """)

def kroger_ingredient_exists(cur, ingredient_name):
    """
    Returns True if there is already at least one row
    for the given ingredient_name in grocery_products.
    """
    cur.execute(
        "SELECT 1 FROM grocery_products WHERE ingredient_name = ? LIMIT 1;",
        (ingredient_name,)
    )
    return cur.fetchone() is not None

def store_kroger_products(ingredient_name, products, cur, conn):
    """
    Inserts flattened Kroger product data into grocery_products table.

    Parameters
    -----------------------
    products: list
        List of flattened product dictionaries with keys:
        - productId (str)
        - brand (str)
        - description (str)
        - categories (str, comma-separated)
        - regularPrice (float or None)
        - promoPrice (float or None)
        - stockLevel (str)
        - fulfillment (str, comma-separated)

    cur: Cursor
        The database cursor object.

    conn: Connection
        The database connection object.

    Returns
    -----------------------
    None
    """

    # Insert each product
    for p in products:
        product_id = p.get("productId")
        brand = p.get("brand")
        description = p.get("description")
        categories = p.get("categories")
        regular_price = p.get("regularPrice")
        promo_price = p.get("promoPrice")
        stock_level = p.get("stockLevel")
        fulfillment = p.get("fulfillment")

        # Check if ingredient already exists
        cur.execute("SELECT 1 FROM grocery_products WHERE ingredient_name = ? LIMIT 1;", (ingredient_name,))
        exists = cur.fetchone()
        if exists:
            continue

        # Insert only if not exists
        cur.execute("""
            INSERT OR REPLACE INTO grocery_products
            (product_id, ingredient_name, brand, description, categories, regular_price, promo_price, stock_level, fulfillment)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            product_id,
            ingredient_name,
            brand,
            description,
            categories,
            regular_price,
            promo_price,
            stock_level,
            fulfillment
        ))

    conn.commit()

def get_kroger_products(ingredient_name):
    json = get_kroger_products_json(ingredient_name)
    return process_kroger_result_json(json)

# for testing independently
if __name__ == "__main__":
    product_list = get_kroger_products("eggs")
    print(product_list)
