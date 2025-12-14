import os
import sqlite3
import requests

# --- API imports ---
from edamam_api import get_edamam_nutrition, store_meal_nutrition, create_edamam_table, create_ingredient_nutrition_table, store_ingredient_nutrition
from kroger_api import get_kroger_products, store_kroger_products, create_grocery_table, kroger_ingredient_exists
from mealdb_api import get_mealdb, process_mealdb_result, create_meal_tables, store_meal, get_all_meals

# --- Calculations ---
from calculations import calculate_average_calories, calculate_recipe_cost, calculate_healthy_available_score

# --- Visualizations (IMPORTANT: this must be at top, not inside main) ---
from visualizations import (
    plot_average_calories,
    plot_recipe_cost,
    plot_healthy_score
)



# FETCH FROM MEALDB & STORE IN DATABASE

def fetch_meal(meal_name, cursor):
    meals_raw = get_mealdb(meal_name)
    meals = process_mealdb_result(meals_raw)

    meal_ids = []   # <- collect IDs

    for meal in meals:
        store_meal(cursor, meal)
        meal_ids.append(meal["id"])  # store IDs

    return meal_ids


# PROCESS NUTRITION + KROGER DATA

def process_meals(cursor, conn):

    meals = get_all_meals(cursor)

    print(f"Found {len(meals)} meals")

    for meal in meals:
        meal_id = meal["id"]
        meal_name = meal["name"]
        print(f"\nProcessing: {meal_name}\n")

        # build ingredient strings WITHOUT duplicates
        ingredient_strings = []
        for ing in meal["ingredients"]:
            name = (ing.get("ingredient") or "").strip()
            measure = (ing.get("measure") or "").strip()
            item = f"{measure} {name}".strip()

            if item not in ingredient_strings:       # prevents repetition
                ingredient_strings.append(item)

        # request calories from Edamam
        nutrition_json = get_edamam_nutrition(ingredient_strings)
        store_ingredient_nutrition(cursor, meal_id, nutrition_json)
        store_meal_nutrition(cursor, meal_id, nutrition_json)

        # request grocery pricing
        for ingredient in meal.get("ingredients", []):
            ingredient_name = (ingredient.get("ingredient") or "").strip()
            if kroger_ingredient_exists(cursor, ingredient_name):
                print(f"Ingredient {ingredient_name} already exists")
                continue
            try:
                product_list = get_kroger_products(ingredient_name)
                print(f"Found {len(product_list)} Kroger products for ingredient {ingredient_name}")
                if (len(product_list) > 0):
                    # store one product for each ingredient
                    store_kroger_products(ingredient_name, product_list[:1], cursor, conn)
            except requests.exceptions.HTTPError:
                print(f"Skipping {ingredient_name} due to server error")

# MAIN PROGRAM

def main():
    db = "final_project.db"
    if os.path.exists(db):
        os.remove(db)
        print("Old database cleared — fresh run\n")

    conn = sqlite3.connect(db)
    cursor = conn.cursor()

    # Create tables if not already existing
    create_grocery_table(cursor)
    create_meal_tables(cursor)
    create_ingredient_nutrition_table(cursor)
    create_edamam_table(cursor)

    # Be careful: Using a general word like "chicken" will result in too many meals getting returned.
    MEALS =  ["arrabiata", "kung pao chicken", "pasta", "cassava", "sushi",
              "brioche", "eggplant adobo", "duck confit", "banana pancakes",
              "kofta burger", "drunken noodles", "coq au vin", "nasi lemak",
              "irish stew", "moussaka", "cassava pizza", "risotto", "enchilada",
              "french onion soup", "carrot cake"]

    for m in MEALS:
        fetch_meal(m, cursor)

    process_meals(cursor, conn)
    conn.commit()

    #  VISUALIZATIONS

    print("\nGenerating graphs...\n")

    # Avg calories by meal
    calories_result = calculate_average_calories(cursor)
    plot_average_calories(calories_result)

    # Ingredient cost visualization
    recipe_cost = calculate_recipe_cost(cursor)
    plot_recipe_cost(recipe_cost)

    # Healthy availability index graph
    healthy_scores = calculate_healthy_available_score(cursor)
    plot_healthy_score(healthy_scores)


    print("\nComplete!")
    conn.close()


if __name__ == "__main__":
    main()
