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

        # Price fields
        price_obj = item.get("price", {})
        regular_price = price_obj.get("regular")
        promo_price = price_obj.get("promo")

        result.append({
            "productId": int(p.get("productId")),
            "description": p.get("description"),
            "regularPrice": regular_price,
            "promoPrice": promo_price
        })

    return result

def create_grocery_table(cur):
    # Create table if it doesn't exist
    cur.execute("""
        CREATE TABLE IF NOT EXISTS grocery_products (
            product_id INTEGER PRIMARY KEY,
            ingredient_name TEXT COLLATE NOCASE,
            description TEXT,
            regular_price REAL,
            promo_price REAL
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
        - productId (integer)
        - description (str)
        - regularPrice (float or None)
        - promoPrice (float or None)

    cur: Cursor
        The database cursor object.

    conn: Connection
        The database connection object.

    Returns
    -----------------------
    None
    """

    if kroger_ingredient_exists(cur, ingredient_name):
        return  # already have this ingredient

    # Insert each product
    for p in products:
        product_id = p.get("productId")
        description = p.get("description")
        regular_price = p.get("regularPrice")
        promo_price = p.get("promoPrice")

        cur.execute("""
            INSERT OR REPLACE INTO grocery_products
            (product_id, ingredient_name, description, regular_price, promo_price)
            VALUES (?, ?, ?, ?, ?)
        """, (
            product_id,
            ingredient_name,
            description,
            regular_price,
            promo_price
        ))

    conn.commit()

def get_kroger_products(ingredient_name):
    products_json = get_kroger_products_json(ingredient_name)
    return process_kroger_result_json(products_json)

# for testing independently
if __name__ == "__main__":
    product_list = get_kroger_products("eggs")
    print(product_list)
