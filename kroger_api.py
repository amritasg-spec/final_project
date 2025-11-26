import base64
import requests

CLIENT_ID = "groceryfinalproject-bbc9kr33"
CLIENT_SECRET = "JUn9T6lrU1-dwEc8PMRhatWssGOuZYLAzLqLIaeT"

def get_access_token():
    token_url = "https://api.kroger.com/v1/connect/oauth2/token"
    
    auth_string = f"{CLIENT_ID}:{CLIENT_SECRET}"
    b64_auth = base64.b64encode(auth_string.encode()).decode()

    headers = {
        "Authorization": f"Basic {b64_auth}",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    data = {
        "grant_type": "client_credentials",
        "scope": "product.compact"
    }

    response = requests.post(token_url, headers=headers, data=data)
    response.raise_for_status()
    return response.json()["access_token"]

def get_kroger_products(query):
    token = get_access_token()

    url = "https://api.kroger.com/v1/products"

    headers = {
        "Authorization": f"Bearer {token}"
    }

    params = {
        "filter.term": query,
        "filter.limit": 5
    }

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()

if __name__ == "__main__":
    print(get_kroger_products("eggs"))

