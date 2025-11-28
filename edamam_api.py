import requests

APP_ID = "my app id"
APP_KEY = "my app key "

def get_edamam_nutrition(ingredient_list):
    url = "https://api.edamam.com/api/nutrition-details"
    
    headers = {
        "Content-Type": "application/json"
    }

    data = {
        "title": "Recipe",
        "ingr": ingredient_list
    }

    params = {
        "app_id": APP_ID,
        "app_key": APP_KEY
    }

    response = requests.post(url, headers=headers, params=params, json=data)

    # this is for unusual ingredients ( i think a 555 error?)
    if response.status_code != 200:
        print(f"Edamam error: {response.status_code}")
        print("Ingredients:", ingredient_list)
        return None 
    
    return response.json()