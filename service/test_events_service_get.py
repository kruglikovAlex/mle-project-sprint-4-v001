import requests

events_store_url = "http://127.0.0.1:8082"

headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
params = {"user_id": 1291250}

resp = requests.post(events_store_url + "/get", headers=headers, params=params)
if resp.status_code == 200:
    result = resp.json()
else:
    result = None
    print(f"status code: {resp.status_code}")
    
print(result) 