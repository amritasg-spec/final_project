import sqlite3
from edamam_api import get_edamam_nutrition, store_edamam_nutrition
from kroger_api import get_kroger_products
#save for wilo func 

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
            health_labels TEXT
        );
    """)

    conn.commit()