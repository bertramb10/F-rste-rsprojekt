import sqlite3

def add_user(name, rfid, pin, access_level):
    conn = sqlite3.connect('access_control.db')
    c = conn.cursor()
    c.execute("INSERT INTO employees (name, rfid, pin, access_level) VALUES (?, ?, ?, ?)",
              (name, rfid, pin, access_level))
    conn.commit()
    conn.close()

if __name__ == '__main__':
    
    add_user('Alice', '1234567890', '1234', 1)
    add_user('Bob', '2345678901', '5678', 2)
    print("Brugere tilføjet")
