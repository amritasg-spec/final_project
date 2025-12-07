import requests

APP_ID = "d34f7e4a"
APP_KEY = "d95639f6e0b93ab57a3291358c365f26"

def get_edamam_nutrition(ingredient_list):

    url = "https://api.edamam.com/api/nutrition-details"
    
    headers = {"Content-Type": "application/json"}

    data = {
        "title": "Recipe",
        "ingr": ingredient_list
    }

    params = {
        "app_id": APP_ID,
        "app_key": APP_KEY
    }

    response = requests.post(url, headers=headers, params=params, json=data)

    if response.status_code != 200:
        print(f"Edamam error: {response.status_code}")
        print("Ingredients:", ingredient_list)
        return None

    return response.json()

def create_edamam_table(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS meal_nutrition (
        meal_id INTEGER PRIMARY KEY,
        calories REAL,
        protein REAL,
        fat REAL,
        carbs REAL,
        sugar REAL,
        fiber REAL,
        sodium REAL,
        diet_labels TEXT,
        health_labels TEXT,
        cuisineType TEXT,
        mealType TEXT,
        dishType TEXT
        );
    """)

def store_edamam_nutrition(cursor, meal_id, nutrition_json):
    if nutrition_json is None:
        return
    total_calories = 0
    total_protein = 0
    total_fat = 0
    total_carbs = 0
    total_sugar = 0
    total_fiber = 0
    total_sodium = 0

    for ing in nutrition_json.get("ingredients", []):
        for parsed in ing.get("parsed", []):
            nutrients = parsed.get("nutrients", {})

            total_calories += nutrients.get("ENERC_KCAL", {}).get("quantity", 0)
            total_protein  += nutrients.get("PROCNT", {}).get("quantity", 0)
            total_fat      += nutrients.get("FAT", {}).get("quantity", 0)
            total_carbs    += nutrients.get("CHOCDF", {}).get("quantity", 0)
            total_sugar    += nutrients.get("SUGAR", {}).get("quantity", 0)
            total_fiber    += nutrients.get("FIBTG", {}).get("quantity", 0)
            total_sodium   += nutrients.get("NA", {}).get("quantity", 0)

    diet_labels = ", ".join(nutrition_json.get("dietLabels", []))
    health_labels = ", ".join(nutrition_json.get("healthLabels", []))
    cuisineType = ", ".join(nutrition_json.get("cuisineType", []))
    mealType = ", ".join(nutrition_json.get("mealType", []))
    dishType = ", ".join(nutrition_json.get("dishType", []))

    cursor.execute("""
        INSERT OR REPLACE INTO meal_nutrition
        (meal_id, calories, protein, fat, carbs, sugar, fiber, sodium,
         diet_labels, health_labels, cuisineType, mealType, dishType)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        meal_id, total_calories, total_protein, total_fat, total_carbs,
        total_sugar, total_fiber, total_sodium,
        diet_labels, health_labels, cuisineType, mealType, dishType
    ))

    print(f"total_calories = {total_calories}")
    print(f"total_protein = {total_protein}")
    print(f"total_fat = {total_fat}")
    print(f"total_carbs = {total_carbs}")
    print(f"total_sugar = {total_sugar}")
    print(f"total_fiber = {total_fiber}")
    print(f"total_sodium = {total_sodium}")
    print(f"Stored Edamam totals for meal {meal_id}")
    print()

