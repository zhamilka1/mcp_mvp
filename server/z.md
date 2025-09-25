import requests

response = requests.post(
    "http://localhost:8000/get_user_info",
    headers={
        "Authorization": "Bearer valid-token"
    },
    json={}  # или {"args": []}, если требуется
)

print(response.json())
