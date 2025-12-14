import sqlite3
import requests

# --- API imports ---
from edamam_api import get_edamam_nutrition, store_meal_nutrition, create_edamam_table, create_ingredient_nutrition_table, store_ingredient_nutrition
from kroger_api import get_kroger_products, store_kroger_products, create_grocery_table, kroger_ingredient_exists
from mealdb_api import get_mealdb, process_mealdb_result, create_meal_tables, store_meal, get_meals_by_ids, search_phrase_exists, add_search_phrase

tables = [
    "ingredients",          # mealdb api
    "grocery_products",     # kroger api
    "ingredient_nutrition", # edamam api
]

def get_row_count(cursor, table_name):
    """
    Returns the number of rows in the specified table.
    """
    cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
    return cursor.fetchone()[0]

def print_table_stats(cursor, tables, before_counts):
    """
    Prints the number of rows added and current total for each table.
    """
    print(f"\n{'Table':<22} {'Rows Added':>15} {'Total':>10}")
    print("-" * 49)
    for table in tables:
        current = get_row_count(cursor, table)
        added = current - before_counts[table]
        print(f"{table:<22} {added:>15} {current:>10}")

def get_all_row_counts(cursor, tables):
    """
    Returns a dict of table_name -> row count.
    """
    return {table: get_row_count(cursor, table) for table in tables}

# FETCH FROM MEALDB & STORE IN DATABASE

def fetch_meal(search_phrase, cursor):
    meals_raw = get_mealdb(search_phrase)
    meals = process_mealdb_result(meals_raw)

    meal_ids = []   # <- collect IDs

    for meal in meals:
        store_meal(cursor, meal)
        meal_ids.append(meal["id"])  # store IDs

    return meal_ids


# PROCESS NUTRITION + KROGER DATA

def process_meals(cursor, conn, meal_ids):

    meals = get_meals_by_ids(cursor, meal_ids)

    print(f"Processing {len(meals)} meals")

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

    conn = sqlite3.connect(db)
    cursor = conn.cursor()

    # Create tables if not already existing
    create_grocery_table(cursor)
    create_meal_tables(cursor)
    create_ingredient_nutrition_table(cursor)
    create_edamam_table(cursor)

    # track number of rows in our tables
    before_counts = get_all_row_counts(cursor, tables)

    # Be careful: Using a general word like "chicken" will result in too many meals getting returned.
    # That will cause us to exceed the max of 25 rows each run.
    all_search_phrases =  [
        "arrabiata", "kung pao chicken", "pasta", "cassava", "sushi",
        "brioche", "eggplant adobo", "duck confit", "banana pancakes",
        "kofta burger", "drunken noodles", "coq au vin", "nasi lemak",
        "irish stew", "moussaka", "risotto", "enchilada",
    ]

    remaining_search_phrases = []
    for search_phrase in all_search_phrases:
        if not search_phrase_exists(cursor, search_phrase):
            remaining_search_phrases.append(search_phrase)

    if len(remaining_search_phrases) != 0:
        search_phrase = remaining_search_phrases[0]
        meal_ids = fetch_meal(search_phrase, cursor)
        add_search_phrase(cursor, search_phrase)
        process_meals(cursor, conn, meal_ids)
        completed = len(all_search_phrases) - len(remaining_search_phrases)
        print_table_stats(cursor, tables, before_counts)
        print(f"\n{completed + 1} of {len(all_search_phrases)} complete. Please run again.")
        conn.commit()
    else:
        print("\nData collection is complete!")
        print("Run visualizations.py to see graphs.")

    conn.close()

if __name__ == "__main__":
    main()
