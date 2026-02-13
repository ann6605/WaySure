import sqlite3

conn = sqlite3.connect('waysure.db')
cursor = conn.cursor()

# Check routes
cursor.execute('SELECT * FROM routes')
routes = cursor.fetchall()

print("📍 ROUTES IN DATABASE:")
for route in routes:
    print(f"   {route[1]} - {route[2]}")

# Check incidents
cursor.execute('SELECT COUNT(*) FROM incidents')
count = cursor.fetchone()[0]
print(f"\n⚠️  TOTAL INCIDENTS: {count}")

conn.close()