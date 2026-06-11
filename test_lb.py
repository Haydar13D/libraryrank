import urllib.request
import json

try:
    req = urllib.request.Request('http://127.0.0.1:8000/api/overview/')
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode())
        lb = data.get('leaderboard', [])
        print("Total in leaderboard:", len(lb))
        for m in lb:
            print(m['role'], m['name'], m['total_p'])
except Exception as e:
    print("Error:", e)
