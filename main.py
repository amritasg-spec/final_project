import os
import sqlite3

# --- API imports ---
from edamam_api import get_edamam_nutrition, store_edamam_nutrition, create_edamam_table
from kroger_api import get_kroger_products, store_kroger_products, create_grocery_table
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

def process_meals(cursor, conn, only_ids=None):

    meals = get_all_meals(cursor)

    if only_ids:
        meals = [m for m in meals if m["id"] in only_ids]

    print(f"\nFound {len(meals)} meals")

    for meal in meals:
        meal_id = meal["id"]
        meal_name = meal["name"]
        print(f"\n🔹 Processing: {meal_name}\n")

        # build ingredient strings WITHOUT duplicates
        ingredient_strings = []
        for ing in meal["ingredients"]:
            name = (ing.get("ingredient") or "").strip()
            measure = (ing.get("measure") or "").strip()
            item = f"{measure} {name}".strip()

            if item not in ingredient_strings:       # prevents repetition
                ingredient_strings.append(item)

        # request calories from Edamam
        nutrition = get_edamam_nutrition(ingredient_strings)
        store_edamam_nutrition(cursor, meal_id, nutrition)

        # request grocery pricing
        for ing in ingredient_strings:
            item = ing.split(" ",1)[-1]  # use ingredient only, not "2 cups ..."
            try:
                products = get_kroger_products(item)
                if products:
                    store_kroger_products(item, products[:1], cursor, conn)
            except Exception as e:
                print(f"⚠ Skipped {item} → {e}")



# MAIN PROGRAM

def main():
    db = "final_project.db"
    if os.path.exists(db):
        os.remove(db)
        print("\n Old database cleared — fresh run\n")

    conn = sqlite3.connect(db)
    cursor = conn.cursor()

    # Create tables if not already existing
    create_grocery_table(cursor)
    create_meal_tables(cursor)
    create_edamam_table(cursor)

    # Meals to run (change freely!)
    MEALS = ["arrabiata"]
    added = []

    for m in MEALS:
        ids = fetch_meal(m, cursor)   # RETURN IDs HERE IF YOU WANT
        added.extend(ids)

    process_meals(cursor, conn, added)  

    for m in MEALS:
        fetch_meal(m, cursor)

    process_meals(cursor, conn)
    conn.commit()

    #  VISUALIZATIONS

    print("\n📊 Generating graphs...\n")

    # Avg calories by meal
    calories_result = calculate_average_calories(cursor)
    plot_average_calories(calories_result)

    # Ingredient cost visualization
    recipe_cost = calculate_recipe_cost(cursor)
    plot_recipe_cost(recipe_cost)

    # Healthy availability index graph
    healthy_scores = calculate_healthy_available_score(cursor)
    plot_healthy_score(healthy_scores)


    print("\n✨ Complete!")
    conn.close()


if __name__ == "__main__":
    main()
