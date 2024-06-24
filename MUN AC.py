import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
import sqlite3
import time
from time import sleep
import threading
from datetime import datetime


GPIO.setmode(GPIO.BOARD)


COLS = [35, 31, 32]  
ROWS = [37, 7, 13, 33]  


for col_pin in COLS:
    GPIO.setup(col_pin, GPIO.OUT)
    GPIO.output(col_pin, GPIO.LOW)


for row_pin in ROWS:
    GPIO.setup(row_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

KEYPAD = [
    ['1', '2', '3'],
    ['4', '5', '6'],
    ['7', '8', '9'],
    ['*', '0', '#']
]


reader = SimpleMFRC522()


conn = sqlite3.connect('access_control.db')
cursor = conn.cursor()


DOOR_LOCK_PIN = 29  
GPIO.setup(DOOR_LOCK_PIN, GPIO.OUT)
GPIO.output(DOOR_LOCK_PIN, GPIO.LOW) 


RED_LED_PIN = 15  
YELLOW_LED_PIN = 5  
GREEN_LED_PIN = 3  
GPIO.setup(RED_LED_PIN, GPIO.OUT)
GPIO.setup(YELLOW_LED_PIN, GPIO.OUT)
GPIO.setup(GREEN_LED_PIN, GPIO.OUT)


BUZZER_PIN = 18
GPIO.setup(BUZZER_PIN, GPIO.OUT)
buzzer_pwm = GPIO.PWM(BUZZER_PIN, 1000)  


buzzer_active = False


DOOR_OPENED_SIGNAL_PIN = 36  
DOOR_LOCKED_SIGNAL_PIN = 38  


GPIO.setup(DOOR_OPENED_SIGNAL_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(DOOR_LOCKED_SIGNAL_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def log_access_attempt(rfid, result):
    """Log an access attempt to the database."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute("INSERT INTO ny_access_log (timestamp, rfid, result) VALUES (?, ?, ?)", (timestamp, rfid, result))
    conn.commit()

def log_event(event_type):
    """Log an event to the database."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    event_type = "åbnet indefra"  
    cursor.execute("INSERT INTO event_log (timestamp, event_type) VALUES (?, ?)", (timestamp, event_type))
    conn.commit()

def unlock_door():
    """Unlock the door."""
    global buzzer_active
    GPIO.output(GREEN_LED_PIN, GPIO.HIGH)  
    GPIO.output(DOOR_LOCK_PIN, GPIO.HIGH)  
    log_event("door_unlocked")

    
    timer_thread = threading.Timer(10.0, start_buzzer)
    timer_thread.start()

    sleep(5)  
    GPIO.output(DOOR_LOCK_PIN, GPIO.LOW)  
    GPIO.output(GREEN_LED_PIN, GPIO.LOW) 
    GPIO.output(RED_LED_PIN, GPIO.HIGH)  
    buzzer_active = False  
    
def start_buzzer():
    """Start the buzzer."""
    global buzzer_active
    buzzer_active = True
    buzzer_pwm.start(50)  

def stop_buzzer():
    """Stop the buzzer."""
    global buzzer_active
    if buzzer_active:
        buzzer_pwm.stop()
        buzzer_active = False

def monitor_door_state():
    """Monitor the door state and control buzzer based on door lock status."""
    global buzzer_active
    door_unlocked_time = None  
    buzzer_stop_timer = None  
    while True:
        door_locked = GPIO.input(DOOR_LOCKED_SIGNAL_PIN)
        if door_locked == GPIO.LOW:  
            if buzzer_active:
                stop_buzzer()
                buzzer_active = False
            if buzzer_stop_timer:
                buzzer_stop_timer.cancel()  
            door_unlocked_time = None  
            GPIO.output(GREEN_LED_PIN, GPIO.LOW)  
        else:  
            if door_unlocked_time is None:
                door_unlocked_time = time.time()  
            else:
                if time.time() - door_unlocked_time >= 10: 
                    if not buzzer_active:
                        start_buzzer()
                        buzzer_active = True
                    
                    if not buzzer_stop_timer:
                        buzzer_stop_timer = threading.Timer(10.0, stop_buzzer)
                        buzzer_stop_timer.start()
                
                while GPIO.input(DOOR_LOCKED_SIGNAL_PIN) == GPIO.HIGH:
                    GPIO.output(GREEN_LED_PIN, GPIO.HIGH)
                    time.sleep(0.5)
                    GPIO.output(GREEN_LED_PIN, GPIO.LOW)
                    time.sleep(0.5)
        sleep(1)  

def get_pin():
    """Get a 4-digit PIN from the keypad."""
    pin = ""
    print("Enter your 4-digit PIN:")
    GPIO.output(RED_LED_PIN, GPIO.LOW) 
    GPIO.output(YELLOW_LED_PIN, GPIO.HIGH)  
    while len(pin) < 4:
        pin += read_keypad()
        print("*", end="", flush=True)
    print()
    GPIO.output(YELLOW_LED_PIN, GPIO.LOW)  
    return pin

def check_access(rfid, pin):
    """Check if the RFID and PIN are correct."""
    cursor.execute("SELECT pin FROM employees WHERE rfid=?", (rfid,))
    result = cursor.fetchone()
    if result is None:
        print("RFID not recognized.")
        return False
    return result[0] == pin

def read_keypad():
    """Read the pressed key from the keypad."""
    pressed_key = None
    while pressed_key is None:
        for col_num, col_pin in enumerate(COLS):
            GPIO.output(col_pin, GPIO.HIGH)
            for row_num, row_pin in enumerate(ROWS):
                if GPIO.input(row_pin) == GPIO.HIGH:
                    pressed_key = KEYPAD[row_num][col_num]
                    while GPIO.input(row_pin) == GPIO.HIGH:
                        pass
                    break
            GPIO.output(col_pin, GPIO.LOW)
            if pressed_key:
                break
    return pressed_key

try:
    GPIO.output(RED_LED_PIN, GPIO.HIGH)  
    
    door_state_thread = threading.Thread(target=monitor_door_state)
    door_state_thread.daemon = True 
    door_state_thread.start()

    while True:
        print("Hold your card near the reader...")
        rfid, text = reader.read()
        print(f"RFID detected: {rfid}")
        cursor.execute("SELECT * FROM employees WHERE rfid=?", (rfid,))
        if cursor.fetchone():
            pin = get_pin()
            if check_access(rfid, pin):
                print("Access granted")
                log_access_attempt(rfid, "granted")
                unlock_door()
            else:
                print("Access denied: Incorrect PIN")
                log_access_attempt(rfid, "denied - incorrect PIN")
        else:
            print("Access denied: Unrecognized RFID")
            log_access_attempt(rfid, "denied - unrecognized RFID")
        sleep(2)
except KeyboardInterrupt:
    pass
finally:
    stop_buzzer()  
    GPIO.cleanup()
    conn.close()
