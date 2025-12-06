import base64
import requests
import os
import sqlite3

APP_KEY = '1'
BASE_URL = f'https://www.themealdb.com/api/json/v1/{APP_KEY}/'

def get_mealdb(query, limit=25):
    url = BASE_URL + 'search.php'
    params = {'s': query}
    response = requests.get(url, params=params)
    response.raise_for_status()
    print(response.json)
    return response.json()
def process_mealdb_result(data):
    meals = data.get("meals", [])
    result = []

    for meal in meals:
        meal_info = {
            "id": meal.get("idMeal"),
            "name": meal.get("strMeal"),
            "category": meal.get("strCategory"),
            "area": meal.get("strArea"),
            "instructions": meal.get("strInstructions"),
            "thumbnail": meal.get("strMealThumb"),
            "tags": meal.get("strTags"),
            "youtube": meal.get("strYoutube"),
            "ingredients": []
        }

        for i in range(1, 21):
            ingredient = meal.get(f"strIngredient{i}")
            measure = meal.get(f"strMeasure{i}")
            if ingredient and ingredient.strip():
                meal_info["ingredients"].append({
                    "ingredient": ingredient,
                    "measure": measure
                })

        result.append(meal_info)
    return result
def create_meal_tables():
    conn = sqlite3.connect("final_project.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS meals (
            id INTEGER PRIMARY KEY,
            name TEXT,
            category TEXT,
            area TEXT,
            instructions TEXT,
            thumbnail TEXT,
            tags TEXT,
            youtube TEXT
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ingredients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            meal_id INTEGER,
            ingredient TEXT,
            measure TEXT,
            FOREIGN KEY (meal_id) REFERENCES meals(id)
        );
    """)  
    conn.commit()
    conn.close()  

def store_meal(cursor, meal):
    cursor.execute("""
        INSERT OR REPLACE INTO meals (id, name, category, area, instructions, thumbnail, tags, youtube)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        meal["id"],
        meal["name"],
        meal["category"],
        meal["area"],
        meal["instructions"],
        meal["thumbnail"],
        meal["tags"],
        meal["youtube"]
    ))

    for ingredient in meal["ingredients"]:
        cursor.execute("""
            INSERT INTO ingredients (meal_id, ingredient, measure)
            VALUES (?, ?, ?)
        """, (
            meal["id"],
            ingredient["ingredient"],
            ingredient["measure"]
        ))



if __name__ == "__main__":
    # 1. Get raw data from API
    raw = get_mealdb("chicken")
    print("Raw API response loaded.")

    # 2. Process the data into cleaned JSON objects
    meals = process_mealdb_result(raw)
    print(f"Processed {len(meals)} meals.")

    conn = sqlite3.connect("final_project.db")
    cursor = conn.cursor()
    create_meal_tables()
    for meal in meals:
        store_meal(cursor, meal)
    conn.commit()
    conn.close()
    print("Meals stored in database.")

