import sqlite3

def delete_user(rfid):
    conn = sqlite3.connect('access_control.db')
    c = conn.cursor()
    c.execute("DELETE FROM employees WHERE rfid=?", (rfid,))
    conn.commit()
    conn.close()
    print(f"Bruger med RFID {rfid} slettet")

if __name__ == '__main__':
    # Eksempel på sletning af en bruger
    rfid_to_delete = '692663892787'
    delete_user(rfid_to_delete)
