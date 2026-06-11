import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'libraryrank.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User

# Create superuser if not exists
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin')

c = Client(HTTP_HOST='127.0.0.1')
c.login(username='admin', password='password') # Wait, I don't know the password.
# Let's force login
user = User.objects.get(username='admin')
c.force_login(user)

# We skip the first request
from django.template.context import BaseContext

original_flatten = BaseContext.flatten

def patched_flatten(self):
    flat = {}
    for d in self.dicts:
        try:
            if hasattr(d, 'flatten') and callable(d.flatten):
                flat.update(d.flatten())
            else:
                flat.update(d)
        except ValueError as e:
            print("=== BAD DICT ===")
            print("Type:", type(d))
            print("Value:", repr(d))
            raise e
    return flat

from django.contrib.messages import constants as message_constants
from django.contrib.messages.storage.fallback import FallbackStorage

request = c.request(**{
    'wsgi.url_scheme': 'http',
    'SERVER_NAME': 'testserver',
    'SERVER_PORT': '80',
    'REQUEST_METHOD': 'GET',
    'PATH_INFO': '/',
})
setattr(request, 'session', c.session)
messages = FallbackStorage(request)
messages.add(message_constants.INFO, "Test message")
request._messages = messages

session = c.session
session['_messages'] = messages.serialize()
session.save()

print("Running with patched flatten...")
try:
    response = c.get('/admin/leaderboard/leveltier/add/')
    print("Status code:", response.status_code)
except Exception as e:
    import traceback
    traceback.print_exc()


