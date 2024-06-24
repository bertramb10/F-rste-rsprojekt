import sqlite3


conn = sqlite3.connect('access_control.db')
cursor = conn.cursor()


cursor.execute('''
    CREATE TABLE IF NOT EXISTS ny_access_log (
        timestamp TEXT,
        rfid TEXT,
        result TEXT
    )
''')


cursor.execute('''
    CREATE TABLE IF NOT EXISTS event_log (
        timestamp TEXT,
        event_type TEXT
    )
''')


conn.commit()
conn.close()
