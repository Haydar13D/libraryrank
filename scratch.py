import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'libraryrank.settings')
django.setup()

from django.test import Client
c = Client(HTTP_HOST='localhost')
r = c.get('/api/pemustaka-teraktif/?role=staff')
print("Status:", r.status_code)
data = r.json()
print("Top Pengunjung Staff Count:", len(data['top_pengunjung']))
if data['top_pengunjung']:
    print("Top Staff 1:", data['top_pengunjung'][0]['name'], data['top_pengunjung'][0]['total_p'])
