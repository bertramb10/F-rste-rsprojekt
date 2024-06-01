import sqlite3

# Opret og initialiser databasen
def init_db():
    conn = sqlite3.connect('access_control.db')
    c = conn.cursor()
    c.execute('''
    CREATE TABLE IF NOT EXISTS employees (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        rfid TEXT NOT NULL UNIQUE,
        pin TEXT NOT NULL,
        access_level INTEGER NOT NULL
    )
    ''')
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print("Database og tabel oprettet.")
