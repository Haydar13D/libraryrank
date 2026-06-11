import urllib.request
import json

data = {
    'member_id': 'L200230051',
    'reward_id': 2
}

payload = json.dumps(data).encode('utf-8')

req = urllib.request.Request(
    'http://127.0.0.1:8000/api/redeem/request-otp/',
    data=payload,
    headers={'Content-Type': 'application/json'}
)

try:
    with urllib.request.urlopen(req) as response:
        res = json.loads(response.read().decode())
        print("RESPONSE SUCCESS:", res)
except urllib.error.HTTPError as e:
    print("HTTP ERROR:", e.code)
    print(e.read().decode())
except Exception as e:
    print("ERROR:", e)
