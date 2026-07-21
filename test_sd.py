from machine import Pin, SPI
import os
import sdcard

spi = SPI(1, baudrate=1000000, sck=Pin(18), mosi=Pin(23), miso=Pin(19))
cs = Pin(5)

sd = sdcard.SDCard(spi, cs)
os.mount(sd, "/sd")

print("Karta SD zamontowana poprawnie!")
print("Zawartosc:", os.listdir("/sd"))

with open("/sd/test.txt", "w") as f:
    f.write("Test zapisu z ESP32 - dziala!\n")

with open("/sd/test.txt", "r") as f:
    print("Odczytana zawartosc pliku:", f.read())