import requests

recommendations_url = "http://127.0.0.1:8080"

headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
params = {"user_id": 5000, 'k': 5}

resp = requests.post(recommendations_url + "/recommendations", headers=headers, params=params)
if resp.status_code == 200:
    recs = resp.json()
else:
    recs = []
    print(f"status code: {resp.status_code}")
    
print(recs) 
