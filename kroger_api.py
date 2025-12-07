import base64
import requests

CLIENT_ID = "groceryfinalproject-bbc9kr33"
CLIENT_SECRET = "JUn9T6lrU1-dwEc8PMRhatWssGOuZYLAzLqLIaeT"

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

        # Convert categories into a comma-separated list
        categories = ", ".join(p.get("categories", []))

        # Price fields
        price_obj = item.get("price", {})
        regular_price = price_obj.get("regular")
        promo_price = price_obj.get("promo")

        # Stock
        stock_level = item.get("inventory", {}).get("stockLevel")

        # Fulfillment: make comma-separated list of properties that are True
        fulfillment = item.get("fulfillment", {})
        fulfillment_str = ", ".join(
            key for key, val in fulfillment.items() if val
        )

        result.append({
            "productId": p.get("productId"),
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
            product_id TEXT PRIMARY KEY,
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
