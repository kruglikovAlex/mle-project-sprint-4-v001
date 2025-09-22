import requests

recommendations_url = "http://127.0.0.1:8080"

headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
params = {"user_id": 1127794, 'k': 3}

resp = requests.post(recommendations_url + "/recommendations_online", headers=headers, params=params)
if resp.status_code == 200:
    online_recs = resp.json()
else:
    online_recs = []
    print(f"status code: {resp.status_code}")    
    
print(online_recs) 