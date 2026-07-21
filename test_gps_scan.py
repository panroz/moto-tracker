from machine import UART
import time

# piny do sprawdzenia jako RX (tu podlaczony jest TX modulu GPS)
# pomijamy 21 i 22 - te sa juz zajete przez MPU6050 (I2C)
candidate_rx_pins = [16, 4, 2, 5, 18, 19, 23, 13, 12, 14, 27, 26, 25, 33, 32, 34, 35, 36, 39]
dummy_tx_pin = 17  # formalnie wymagany przez UART, realnie nieuzywany (nic nie wysylamy do GPS)

found = False
for rx_pin in candidate_rx_pins:
    try:
        uart = UART(1, baudrate=9600, rx=rx_pin, tx=dummy_tx_pin, timeout=1000)
        time.sleep(1)
        data = uart.read()
        if data and b'$' in data:
            print(f"RX={rx_pin} -> ZNALEZIONO dane GPS: {data[:80]}")
            found = True
        else:
            print(f"RX={rx_pin} -> brak danych")
    except Exception as e:
        print(f"RX={rx_pin} -> blad: {e}")
    time.sleep(0.2)

if not found:
    print("Nic nie znaleziono. Sprawdz czy modul GPS ma zasilanie (VCC/GND) i czy dioda na module miga.")