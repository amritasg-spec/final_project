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
    return response.json()

def process_mealdb_result(data):
    # No results for this term → skip
    if not data or data.get("meals") is None:
        return []

    meals = data["meals"]
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
                    "ingredient": ingredient.strip(),
                    "measure": (measure or "").strip()
                })

        #goddamn duplicate ingredients bruh im gonna crash out 
        seen = set()
        unique = []
        for ing in meal_info["ingredients"]:
            key = ing["ingredient"].lower()
            if key not in seen:
                seen.add(key)
                unique.append(ing)
        meal_info["ingredients"] = unique

        result.append(meal_info)

    return result

def create_meal_tables(cursor):
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

    # table for tracking our progress
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS progress_tracking (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            search_phrase TEXT UNIQUE
        )
    """)

def search_phrase_exists(cur, search_phrase):
    """
    Progress tracking: Returns True if the search_phrase is already complete.
    """
    cur.execute(
        "SELECT 1 FROM progress_tracking WHERE search_phrase = ? LIMIT 1;",
        (search_phrase,)
    )
    return cur.fetchone() is not None

def add_search_phrase(cur, search_phrase):
    """
    Progress tracking: Sets search_phrase as already complete by inserting it into the progress_tracking table.
    """
    cur.execute(
        "INSERT OR IGNORE INTO progress_tracking (search_phrase) VALUES (?);",
        (search_phrase,)
    )

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

def get_meals_by_ids(cursor, meal_ids):
    """
    Returns a list of meal objects.
    Each meal object has: id, name, ingredients[].
    """
    if not meal_ids:
        return []

    placeholders = ",".join("?" * len(meal_ids))
    cursor.execute(f"SELECT id, name FROM meals WHERE id IN ({placeholders}) ORDER BY id;", meal_ids)
    meal_rows = cursor.fetchall()

    meals = []

    for meal_id, name in meal_rows:
        # Fetch ingredients for this meal
        cursor.execute(
            "SELECT ingredient, measure FROM ingredients WHERE meal_id = ? ORDER BY id;",
            (meal_id,)
        )
        ingredient_rows = cursor.fetchall()

        meal = {
            "id": meal_id,
            "name": name,
            "ingredients": [
                {"ingredient": ing, "measure": measure}
                for ing, measure in ingredient_rows
            ]
        }

        meals.append(meal)

    return meals

if __name__ == "__main__":
    # 1. Get raw data from API
    raw = get_mealdb("fish")
    print("Raw API response loaded.")

    # 2. Process the data into cleaned JSON objects
    meals = process_mealdb_result(raw)
    print(f"Processed {len(meals)} meals.")

    conn = sqlite3.connect("final_project.db")
    cursor = conn.cursor()
    create_meal_tables(cursor)
    for meal in meals:
        store_meal(cursor, meal)
    conn.commit()
    conn.close()
    print("Meals stored in database.")

