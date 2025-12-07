import sqlite3

conn = sqlite3.connect("final_project.db")
cursor = conn.cursor()

print("\n--- MEALS ---")
cursor.execute("SELECT idMeal, strMeal, strCategory FROM meals LIMIT 10;")
print(cursor.fetchall())

print("\n--- NUTRITION ---")
cursor.execute("SELECT meal_id, calories, protein FROM meal_nutrition LIMIT 10;")
print(cursor.fetchall())

print("\n--- INGREDIENTS ---")
cursor.execute("SELECT meal_id, ingredient_name FROM ingredients LIMIT 10;")
print(cursor.fetchall())

print("\n--- KROGER DATA ---")
cursor.execute("SELECT ingredient_name, description FROM grocery_products LIMIT 10;")
print(cursor.fetchall())

conn.close()

