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


def store_edamam_nutrition(cursor, meal_id, nutrition_json):

    if nutrition_json is None:
        return

    calories = nutrition_json.get("calories")
    nutrients = nutrition_json.get("totalNutrients", {})

    protein = nutrients.get("PROCNT", {}).get("quantity")
    fat = nutrients.get("FAT", {}).get("quantity")
    carbs = nutrients.get("CHOCDF", {}).get("quantity")
    sugar = nutrients.get("SUGAR", {}).get("quantity")
    fiber = nutrients.get("FIBTG", {}).get("quantity")
    sodium = nutrients.get("NA", {}).get("quantity")

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
    meal_id, calories, protein, fat, carbs, sugar, fiber, sodium,
    diet_labels, health_labels, cuisineType, mealType, dishType
    ))

