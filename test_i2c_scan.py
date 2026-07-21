from machine import Pin, I2C

# typowe pary pinow uzywane na plytkach ESP32 DevKit
pin_pairs = [
    (21, 22),  # najbardziej typowy uklad (SDA, SCL)
    (22, 21),
    (4, 5),
    (5, 4),
]

found = False
for sda, scl in pin_pairs:
    try:
        i2c = I2C(0, sda=Pin(sda), scl=Pin(scl), freq=100000)
        devices = i2c.scan()
        if devices:
            print(f"SDA={sda}, SCL={scl} -> znaleziono urzadzenia: {[hex(d) for d in devices]}")
            found = True
        else:
            print(f"SDA={sda}, SCL={scl} -> brak urzadzen")
    except Exception as e:
        print(f"SDA={sda}, SCL={scl} -> blad: {e}")

if not found:
    print("Nie znaleziono zadnego urzadzenia I2C na sprawdzonych parach pinow.")