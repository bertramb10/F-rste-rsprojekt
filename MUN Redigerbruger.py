import sqlite3

def edit_user(rfid, name=None, pin=None, access_level=None):
    conn = sqlite3.connect('access_control.db')
    c = conn.cursor()
    if name:
        c.execute("UPDATE employees SET name=? WHERE rfid=?", (name, rfid))
    if pin:
        c.execute("UPDATE employees SET pin=? WHERE rfid=?", (pin, rfid))
    if access_level is not None:
        c.execute("UPDATE employees SET access_level=? WHERE rfid=?", (access_level, rfid))
    conn.commit()
    conn.close()
    print(f"Bruger med RFID {rfid} redigeret")

if __name__ == '__main__':
    
    rfid_to_edit = '692663892787'
    new_name = 'Christian Brose'
    new_pin = '1111'
    new_access_level = 1
    edit_user(rfid_to_edit, name=new_name, pin=new_pin, access_level=new_access_level)
