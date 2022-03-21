from os import path
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
# print(ROOT_DIR)
STATIC_FILES_DIR = path.join(ROOT_DIR, 'staticfiles')
# print(STATIC_FILES_DIR)
STATIC_URL = '/static/'