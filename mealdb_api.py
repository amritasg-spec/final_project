import base64
import requests
import os
import sqlite3

APP_KEY = '1'
BASE_URL = f'https://www.themealdb.com/api/json/v1/{APP_KEY}/'

def get_mealdb(query):
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



if __name__ == "__main__":
    # 1. Get raw data from API
    raw = get_mealdb("chicken")
    print("Raw API response loaded.")

    # 2. Process the data into cleaned JSON objects
    meals = process_mealdb_result(raw)
    print(f"Processed {len(meals)} meals.")

