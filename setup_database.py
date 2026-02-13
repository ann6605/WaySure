import sqlite3
from datetime import datetime, timedelta


conn = sqlite3.connect('waysure.db')
cursor = conn.cursor()

print("🔧 Creating database...")

# Create Routes Table (stores bus/train routes)
cursor.execute('''
    CREATE TABLE IF NOT EXISTS routes (
        route_id INTEGER PRIMARY KEY,
        route_number TEXT,
        route_name TEXT,
        start_location TEXT,
        end_location TEXT,
        distance_km REAL,
        avg_duration_mins INTEGER
    )
''')
print("✅ Routes table created")

# Create Incidents Table (stores safety reports)
cursor.execute('''
    CREATE TABLE IF NOT EXISTS incidents (
        incident_id INTEGER PRIMARY KEY,
        route_id INTEGER,
        incident_type TEXT,
        severity TEXT,
        description TEXT,
        latitude REAL,
        longitude REAL,
        reported_at TEXT
    )
''')
print("✅ Incidents table created")

# Create Users Table (stores user accounts)
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        email TEXT,
        phone_number TEXT
    )
''')
print("✅ Users table created")

# Create Panic Alerts Table (stores emergency alerts)
cursor.execute('''
    CREATE TABLE IF NOT EXISTS panic_alerts (
        alert_id INTEGER PRIMARY KEY,
        user_id INTEGER,
        latitude REAL,
        longitude REAL,
        alert_time TEXT,
        status TEXT
    )
''')
print("✅ Panic alerts table created")


routes = [
    (1, '45B', 'City Center to Tech Park', 'Central Station', 'Tech Park', 12.5, 35),
    (2, '12A', 'University Line', 'University Gate', 'Mall Road', 8.3, 25),
    (3, '78C', 'Airport Express', 'Airport Terminal', 'Railway Station', 18.7, 45),
    (4, '23X', 'Beach Route', 'Marina Beach', 'Shopping District', 6.2, 20),
    (5, '56D', 'Industrial Line', 'Industrial Area', 'Downtown', 15.4, 40),
]

for route in routes:
    cursor.execute('''
        INSERT OR IGNORE INTO routes VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', route)

print("✅ Sample routes added")

# Add sample incidents (for testing safety scores)
incidents = [
    (1, 1, 'theft', 'high', 'Phone stolen', 10.8231, 76.2711, '2025-02-11 10:30:00'),
    (2, 1, 'harassment', 'medium', 'Verbal abuse', 10.8245, 76.2725, '2025-02-09 18:45:00'),
    (3, 2, 'overcrowding', 'low', 'Very crowded bus', 10.8156, 76.2844, '2025-02-08 09:15:00'),
    (4, 3, 'accident', 'high', 'Minor collision', 10.8478, 76.2712, '2025-01-30 14:20:00'),
    (5, 4, 'theft', 'medium', 'Bag snatching', 10.8234, 76.2899, '2025-02-10 20:00:00'),
]

for incident in incidents:
    cursor.execute('''
        INSERT OR IGNORE INTO incidents VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', incident)

print("✅ Sample incidents added")


cursor.execute('''
    INSERT OR IGNORE INTO users VALUES (1, 'demo_user', 'demo@waysure.com', '+919876543210')
''')
print("✅ Demo user added")

conn.commit()
conn.close()

print("\n🎉 DATABASE READY! File created: waysure.db")
print("📊 You have:")
print("   - 5 routes")
print("   - 5 incidents") 
print("   - 1 demo user")