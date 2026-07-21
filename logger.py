from machine import Pin, SPI, I2C, UART
import os
import sdcard
import time

# --- MPU6050 (I2C) ---
MPU_ADDR = 0x68
i2c = I2C(0, sda=Pin(21), scl=Pin(22), freq=100000)
i2c.writeto_mem(MPU_ADDR, 0x6B, b'\x00')  # wybudzenie z trybu snu

def read_word(reg):
    high = i2c.readfrom_mem(MPU_ADDR, reg, 1)[0]
    low = i2c.readfrom_mem(MPU_ADDR, reg + 1, 1)[0]
    value = (high << 8) | low
    if value >= 0x8000:
        value -= 0x10000
    return value

# --- GPS (UART) ---
gps_uart = UART(1, baudrate=9600, rx=16, tx=17, timeout=100)
gps_buffer = b""
last_lat = None
last_lon = None
gps_valid = False

def update_gps():
    global gps_buffer, last_lat, last_lon, gps_valid
    if gps_uart.any():
        gps_buffer += gps_uart.read()
        while b"\n" in gps_buffer:
            line, gps_buffer = gps_buffer.split(b"\n", 1)
            try:
                line = line.decode("ascii", "ignore").strip()
            except Exception:
                continue
            if line.startswith("$GPRMC"):
                parts = line.split(",")
                if len(parts) > 6 and parts[2] == "A":
                    lat_raw, lat_dir = parts[3], parts[4]
                    lon_raw, lon_dir = parts[5], parts[6]
                    if lat_raw and lon_raw:
                        lat = float(lat_raw[:2]) + float(lat_raw[2:]) / 60
                        if lat_dir == "S":
                            lat = -lat
                        lon = float(lon_raw[:3]) + float(lon_raw[3:]) / 60
                        if lon_dir == "W":
                            lon = -lon
                        last_lat, last_lon = lat, lon
                        gps_valid = True

# --- SD (SPI) ---
spi = SPI(1, baudrate=1000000, sck=Pin(18), mosi=Pin(23), miso=Pin(19))
cs = Pin(5)
sd = sdcard.SDCard(spi, cs)
os.mount(sd, "/sd")

log_filename = "/sd/log_{}.csv".format(time.ticks_ms())
with open(log_filename, "w") as f:
    f.write("timestamp_ms,accel_x,accel_y,accel_z,gyro_x,gyro_y,gyro_z,lat,lon,gps_valid\n")

print("Logowanie do pliku:", log_filename)

buffer = []
BUFFER_FLUSH_SIZE = 20   # co ok. 2 sekundy przy 10Hz
SAMPLE_INTERVAL_MS = 100  # 10 odczytow na sekunde

last_sample_time = time.ticks_ms()

while True:
    now = time.ticks_ms()
    if time.ticks_diff(now, last_sample_time) >= SAMPLE_INTERVAL_MS:
        last_sample_time = now

        accel_x = read_word(0x3B)
        accel_y = read_word(0x3D)
        accel_z = read_word(0x3F)
        gyro_x = read_word(0x43)
        gyro_y = read_word(0x45)
        gyro_z = read_word(0x47)

        row = "{},{},{},{},{},{},{},{},{},{}".format(
            now, accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z,
            last_lat if last_lat is not None else "",
            last_lon if last_lon is not None else "",
            1 if gps_valid else 0
        )
        buffer.append(row)

        if len(buffer) >= BUFFER_FLUSH_SIZE:
            with open(log_filename, "a") as f:
                f.write("\n".join(buffer) + "\n")
            print("Zapisano", len(buffer), "wpisow")
            buffer = []

    update_gps()