import sqlite3

# Opret forbindelse til databasen
conn = sqlite3.connect('access_control.db')
cursor = conn.cursor()

# Opret tabel til adgangslogning
cursor.execute('''
    CREATE TABLE IF NOT EXISTS ny_access_log (
        timestamp TEXT,
        rfid TEXT,
        result TEXT
    )
''')

# Opret tabel til hændelseslogning
cursor.execute('''
    CREATE TABLE IF NOT EXISTS event_log (
        timestamp TEXT,
        event_type TEXT
    )
''')

# Gem ændringer og luk forbindelsen til databasen
conn.commit()
conn.close()
