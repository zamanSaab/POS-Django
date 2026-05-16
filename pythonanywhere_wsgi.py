"""
Paste this content into the WSGI configuration file on PythonAnywhere.
Path: /var/www/zaman07_pythonanywhere_com_wsgi.py
"""
import os
import sys

# Add your project to the Python path
path = "/home/zaman07/POS-Django"
if path not in sys.path:
    sys.path.insert(0, path)

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv(os.path.join(path, ".env"))

os.environ["DJANGO_SETTINGS_MODULE"] = "config.settings.pythonanywhere"

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
