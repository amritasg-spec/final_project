import sqlite3
#ok so we have 3 main calculations i think, idk if we need more for extra cred but we can discuss that later

#calculation 1: average calories per meal
def calculate_average_calories(cursor): 
    cursor.execute("""
        SELECT meals.category, AVG(meal_nutrition.calories)
        FROM meal_nutrition
        JOIN meals ON meals.id = meal_nutrition.meal_id
        GROUP BY meals.category;
    """)

    results = cursor.fetchall()
    return {row[0]: row[1] for row in results}

#calculation 2: estimated grocery cost per recipe 
def calculate_recipe_cost(cursor):
    cursor.execute("""
        SELECT ingredients.meal_id,
               SUM(COALESCE(grocery_products.regular_price, 0))
        FROM ingredients
        LEFT JOIN grocery_products
            ON ingredients.ingredient = grocery_products.ingredient_name
        GROUP BY ingredients.meal_id;
    """)

    results = cursor.fetchall()
    return {row[0]: row[1] for row in results}

#calculation 3: healthy + availible score (idk what this means)
def calculate_healthy_available_score(cursor):
    cursor.execute("""
        SELECT meal_id, calories, protein, fat, carbs, sugar, fiber, sodium
        FROM meal_nutrition
    """)

    results = cursor.fetchall()
    scores = {}

    for meal_id, cal, pro, fat, carb, sugar, fiber, sodium in results:

        # Normalize & weight scoring categories (0-10 scale)
        protein_score = min(pro / 20, 10)
        fiber_score = min(fiber / 8, 10)
        sugar_penalty = max(10 - (sugar / 5), 0)
        sodium_penalty = max(10 - (sodium / 500), 0)

        # Final composite score (0–10)
        score = round((protein_score + fiber_score + sugar_penalty + sodium_penalty) / 4, 2)

        scores[meal_id] = score
    
    return scores


if __name__ == "__main__":
    conn = sqlite3.connect("final_project.db")
    cursor = conn.cursor()

    avg_calories = calculate_average_calories(cursor)
    for category, cal in avg_calories.items():
        print(f"{category}: {cal:.2f} kcal")
    conn.close()