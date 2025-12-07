import os
import sqlite3
from edamam_api import get_edamam_nutrition, store_edamam_nutrition, create_edamam_table
from kroger_api import get_kroger_products, store_kroger_products, create_grocery_table
from mealdb_api import get_mealdb, process_mealdb_result, create_meal_tables, store_meal, get_all_meals
from calculations import calculate_average_calories, calculate_recipe_cost, calculate_healthy_available_score

def fetch_meal(meal_name, cursor):
    # get and store meals and ingredients
    meals_raw = get_mealdb(meal_name)
    meals = process_mealdb_result(meals_raw)
    for meal in meals:
        store_meal(cursor, meal)

def process_meals(cursor, conn):
    # get all meals from the database
    all_meals = get_all_meals(cursor)
    print(f"Found {len(all_meals)} meals")
    print(all_meals)
    print()

    # for each meal get and store nutrition
    for meal in all_meals:
        meal_id = meal["id"]
        meal_name = meal["name"]

        print()
        print(f"Processing {meal_name} *******************")
        print()

        # to call Edamam, build ingredient strings in the form: "measure ingredient"
        ingredient_strings = []
        for ingredient in meal.get("ingredients", []):
            measure = (ingredient.get("measure") or "").strip()
            name = (ingredient.get("ingredient") or "").strip()
            if measure and name:
                ingredient_strings.append(f"{measure} {name}")
            elif name:
                ingredient_strings.append(name)
            elif measure:
                ingredient_strings.append(measure)

        # skip meals with no usable ingredients
        if not ingredient_strings:
            continue

        # call Edamam and store the total nutrition for the meal
        nutrition = get_edamam_nutrition(ingredient_strings)
        store_edamam_nutrition(cursor, meal_id, nutrition)

        # call Kroger to get and store prices for each ingredient
        for ingredient in meal.get("ingredients", []):
            ingredient_name = (ingredient.get("ingredient") or "").strip()
            product_list = get_kroger_products(ingredient_name)
            print(f"Found {len(product_list)} Kroger products for ingredient {ingredient_name}")
            if (len(product_list) > 0):
                # store one product for each ingredient
                store_kroger_products(ingredient_name, product_list[:1], cursor, conn)
        print()

def main():
    db_path = "final_project.db"

    # remove existing database as we will re-create it
    if os.path.exists(db_path):
        os.remove(db_path)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # create tables
    create_grocery_table(cursor)
    create_meal_tables(cursor)
    create_edamam_table(cursor)

    # add meals to the database
    fetch_meal("arrabiata", cursor,)
    fetch_meal("pasta", cursor)
    fetch_meal("kung pao chicken", cursor)

    # process meals
    process_meals(cursor, conn)

    # save all database inserts
    conn.commit()

    # calculations
    print("Average calories calculation")
    calories_result = calculate_average_calories(cursor)
    print(calories_result)
    print()

    print("Cost calculation")
    recipe_cost = calculate_recipe_cost(cursor)
    print(recipe_cost)
    print()
    # calculate_healthy_available_score(cursor)

    # close database connection
    conn.close()

if __name__ == "__main__":
    main()
