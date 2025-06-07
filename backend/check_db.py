import sqlite3
import json

conn = sqlite3.connect('fto_navigator.db')
cursor = conn.cursor()

# Show all analyses
cursor.execute("SELECT id, title, status, created_at FROM research_analyses")
print("All Analyses:")
print("-" * 80)
for row in cursor.fetchall():
    print(f"ID: {row[0][:8]}... | Title: {row[1][:30]}... | Status {row[2]} | Created: {row[3]}")

conn.close()