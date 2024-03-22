import requests
import random
import string
import time

api_endpoint = "http://127.0.0.1:5000/"  # replace with api_endpoint

for i in range(random.randint(5, 10)):
    name = ''.join(random.choice(string.ascii_letters) for _ in range(random.randint(5, 10)))
    data = {
        "name": name.title(),
        "phone": f"{random.randint(100000000, 999999999)}",
        "email": f"{name.lower()}@gmail.com",
        "password": f"{name.lower()}9876"
    }
    registered = requests.post(f"{api_endpoint}register", json=data)
    time.sleep(0.1)
    response = requests.post(f"{api_endpoint}login", json=data)
    if response.status_code == 200:
        data = response.json()
        headers = {
            "Authorization": f"Bearer {data.get('access_token')}"
        }
        name = ''.join(random.choice(string.ascii_letters) for _ in range(random.randint(5, 10)))
        phone = random.randint(100000000, 999999999)
        data = {
            "name": name.title(),
            "phone": f"{phone}"
        }
        contact_response = requests.post(f"{api_endpoint}add-contact", headers=headers, json=data)
        time.sleep(0.1)
        data = {
            "phone": f"{random.randint(phone, 999999999)}"
        }
        spam_response = requests.post(f"{api_endpoint}mark-spam", headers=headers, json=data)
        time.sleep(0.2)
        logout_response = requests.post(f"{api_endpoint}logout", headers=headers, json=data)
        time.sleep(0.2)
    time.sleep(0.3)
    print("Random Data Generated")
