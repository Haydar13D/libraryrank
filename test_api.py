import urllib.request
import json

try:
    req = urllib.request.Request('http://127.0.0.1:8000/api/pemustaka-teraktif/?role=staff&date_from=&date_to=&q=')
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode())
        print("Visitors:", len(data.get('top_pengunjung', [])))
        print("Borrowers:", len(data.get('top_peminjam', [])))
        if data.get('top_pengunjung'):
            print("First visitor:", data['top_pengunjung'][0]['name'])
except Exception as e:
    print("Error:", e)
