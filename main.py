import sqlite3
from edamam_api import get_edamam_nutrition, store_edamam_nutrition
from kroger_api import get_kroger_products
from mealdb_api import create_meal_tables, store_meal

def main():
    conn = sqlite3.connect("final_project.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS meal_nutrition (
        meal_id INTEGER PRIMARY KEY,
        calories REAL,
        protein REAL,
        fat REAL,
        carbs REAL,
        sugar REAL,
        fiber REAL,
        sodium REAL,
        diet_labels TEXT,
        health_labels TEXT,
        cuisineType TEXT,
        mealType TEXT,
        dishType TEXT
        );
    """)
    

        
    ingredients = ["2 eggs", "1 cup milk", "1 tbsp sugar"]
    nutrition = get_edamam_nutrition(ingredients)
    store_edamam_nutrition(cursor, 1, nutrition)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    main()