import os
from pathlib import Path

BASE_DIR = Path(r'E:\Inventory')
SETTINGS_PATH = BASE_DIR / 'config' / 'settings.py'

with open(SETTINGS_PATH, 'r', encoding='utf-8') as f:
    content = f.read()

apps_str = '''
    'widget_tweaks',
    'apps.accounts',
    'apps.products',
    'apps.inventory',
    'apps.orders',
    'apps.suppliers',
    'apps.fabrics',
    'apps.dashboard',
'''
content = content.replace(\"'django.contrib.staticfiles',\", \"'django.contrib.staticfiles',\" + apps_str)

templates_dirs = \"'DIRS': [BASE_DIR / 'templates'],\"
content = content.replace(\"'DIRS': [],\", templates_dirs)

extra_config = '''

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

AUTH_USER_MODEL = 'accounts.User'
'''
content += extra_config

with open(SETTINGS_PATH, 'w', encoding='utf-8') as f:
    f.write(content)
