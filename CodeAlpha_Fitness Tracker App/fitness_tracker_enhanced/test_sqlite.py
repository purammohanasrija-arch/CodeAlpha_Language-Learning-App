import sqlite3

conn = sqlite3.connect("fitness.db")

print("Database Created Successfully")

conn.close()