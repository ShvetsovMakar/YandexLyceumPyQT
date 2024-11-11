import sqlite3

db = sqlite3.connect("database/tasks.db")
cur = db.cursor()
