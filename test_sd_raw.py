from machine import Pin, SoftSPI
import time

spi = SoftSPI(baudrate=100000, polarity=0, phase=0, sck=Pin(18), mosi=Pin(23), miso=Pin(19))
cs = Pin(5, Pin.OUT)
cs.value(1)

spi.write(bytes([0xFF] * 10))
time.sleep(0.1)

cs.value(0)
cmd0 = bytes([0x40, 0x00, 0x00, 0x00, 0x00, 0x95])
spi.write(cmd0)

response = bytearray(8)
spi.readinto(response)
cs.value(1)

print("Odpowiedz karty (surowe bajty):", [hex(b) for b in response])