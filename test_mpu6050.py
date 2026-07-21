from machine import Pin, I2C
import time

MPU_ADDR = 0x68
i2c = I2C(0, sda=Pin(21), scl=Pin(22), freq=100000)

# wybudzenie MPU6050 z trybu snu (domyslnie jest usypiany)
i2c.writeto_mem(MPU_ADDR, 0x6B, b'\x00')

def read_word(reg):
    high = i2c.readfrom_mem(MPU_ADDR, reg, 1)[0]
    low = i2c.readfrom_mem(MPU_ADDR, reg + 1, 1)[0]
    value = (high << 8) | low
    if value >= 0x8000:
        value -= 0x10000
    return value

while True:
    accel_x = read_word(0x3B)
    accel_y = read_word(0x3D)
    accel_z = read_word(0x3F)
    gyro_x = read_word(0x43)
    gyro_y = read_word(0x45)
    gyro_z = read_word(0x47)

    print(f"Accel: X={accel_x} Y={accel_y} Z={accel_z}  Gyro: X={gyro_x} Y={gyro_y} Z={gyro_z}")
    time.sleep(0.5)