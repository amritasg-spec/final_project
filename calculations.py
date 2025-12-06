import sqlite3
#ok so we have 3 main calculations i think, idk if we need more for extra cred but we can discuss that later

#calculation 1: average calories per meal
def calculate_average_calories(cursor): 
    cursor.execute("""
        SELECT meals.strCategory, AVG(meal_nutrition.calories)
        FROM meal_nutrition
        JOIN meals ON meals.idMeal = meal_nutrition.meal_id
        GROUP BY meals.strCategory;
    """)

    results = cursor.fetchall()
    return {row[0]: row[1] for row in results}

#calculation 2: estimated grocery cost per recipe 
def calculate_recipe_cost(cursor):
    cursor.execute("""
        SELECT ingredients.meal_id, AVG(grocery_products.price)
        FROM ingredients
        JOIN grocery_products 
        ON ingredients.ingredient_name = grocery_products.name
        GROUP BY ingredients.meal_id;
    """)

    results = cursor.fetchall()
    return {row[0]: row[1] for row in results}

#calculation 3: healthy + availible score (idk what this means)
def calculate_healthy_available_score(cursor):
    cursor.execute("""
        SELECT m.meal_id,
               COUNT(g.productId) AS available_ingredients,
               LENGTH(n.health_labels) - LENGTH(REPLACE(n.health_labels, ',', '')) + 1 AS health_count
        FROM ingredients m
        LEFT JOIN grocery_products g 
             ON m.ingredient_name = g.description
        JOIN meal_nutrition n 
             ON m.meal_id = n.meal_id
        GROUP BY m.meal_id;
    """)

    results = cursor.fetchall()
    return {row[0]: row[1] + row[2] for row in results}