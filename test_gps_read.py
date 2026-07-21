from machine import UART
import time

uart = UART(1, baudrate=9600, rx=16, tx=17, timeout=1000)

print("Nasluchuje danych z GPS (Ctrl+C / Stop zeby przerwac)...")
for i in range(10):
    time.sleep(1)
    if uart.any():
        data = uart.read(200)
        print(data)
    else:
        print("brak danych w tej sekundzie")