import os

USE_SQLITE = os.environ.get("USE_SQLITE", "false").lower() == "true"

if USE_SQLITE:
    DB_URI = 'sqlite:///database/sqlite/dev.sqlite3'
else:
    DB_URI = 'postgresql://aqoonta_user:password123@localhost/aqoonta'