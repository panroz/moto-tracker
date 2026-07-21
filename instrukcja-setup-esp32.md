# Instrukcja: konfiguracja ESP32 od zera (moto-tracker)

Ta instrukcja zakłada nowy komputer z systemem Windows, na którym nic jeszcze nie jest zainstalowane, oraz świeżo rozpakowaną płytkę ESP32-WROOM-32S DevKit z podłączonymi czujnikami (MPU6050, GPS NEO-7M, moduł microSD).

## Czego będziesz potrzebować
- Komputer z Windows
- Kabel USB Type-C
- Płytka ESP32-WROOM-32S DevKit z podłączonymi czujnikami
- Konto na GitHub (https://github.com)

---

## Lista podzespołów

| # | Podzespół | Opis |
|---|---|---|
| 1 | ESP32-WROOM-32S DevKit | 30-pin, Type-C, chip D0WD/D0WDQ6 |
| 2 | GY-521 (MPU6050) | 3-osiowy żyroskop + akcelerometr, I2C |
| 3 | GY-GPSU3-NEO (NEO-7M) | Moduł GPS, UART |
| 4 | Moduł karty microSD | Interfejs SPI |
| 5 | TP4056 | Moduł ładowania baterii Li-ion, USB Type-C, 1A, z ochroną |
| 6 | MT3608 | Moduł boost DC-DC 2A (podwyższanie napięcia z baterii do 5V) |
| 7 | Bateria XHZ 104050 | Li-ion 3.7V, 2500mAh |
| 8 | Metalowy przycisk z zatrzaskiem | Podświetlana obwódka (symbol power), 5 przewodów — 2 do styku przełącznika, 3 do LED |

## Schemat podłączenia do ESP32

**Czujniki i karta SD:**

| Podzespół | Pin podzespołu | Pin ESP32 |
|---|---|---|
| MPU6050 (I2C) | VCC | 3V3 |
| | GND | GND |
| | SDA | GPIO21 |
| | SCL | GPIO22 |
| GPS NEO-7M (UART) | VCC | 3V3 |
| | GND | GND |
| | TX | GPIO16 (RX) |
| | RX | GPIO17 (TX) |
| Moduł microSD (SPI) | 3V3 / VCC | 3V3 *(nie 5V — sprawdź oznaczenie na module)* |
| | GND | GND |
| | CS | GPIO5 |
| | MOSI | GPIO23 |
| | CLK / SCK | GPIO18 |
| | MISO | GPIO19 |
| Przycisk start/stop | czarny (styk) | GND |
| | czerwony (styk) | GPIO4 |

> Zielony/niebieski/żółty przewód przycisku (LED podświetlenia) — do podłączenia przy montażu finalnym, nie są potrzebne do samej funkcji start/stop.

**Łańcuch zasilania (bateria → ESP32):**

```
Bateria Li-ion 3.7V (XHZ 104050)
    → TP4056 (ładowanie przez Type-C + ochrona)
    → MT3608 (boost 3.7V → 5V)
    → ESP32 pin VIN (5V) lub VUSB
```

> Uwaga: MT3608 pobiera prąd stale, nawet gdy ESP32 jest w trybie uśpienia — ma to znaczenie przy planowaniu czasu pracy na baterii.

Wszystkie piny w tabeli powyżej zostały praktycznie zweryfikowane (skan I2C, testy UART/SPI, pomiary multimetrem) na naszym zestawie. Jeśli montujesz nowy egzemplarz, warto to i tak zweryfikować samodzielnie, zamiast zakładać identyczne okablowanie.

---

## 1. Instalacja Thonny (środowisko do programowania w Pythonie)

1. Wejdź na https://thonny.org
2. Pobierz i zainstaluj wersję dla Windows (domyślne ustawienia instalatora są OK)

## 2. Instalacja Gita

1. Wejdź na https://git-scm.com/downloads/win
2. Pobierz instalator (64-bit Git for Windows), uruchom go
3. Klikaj "Next" na każdym oknie, zostaw domyślne opcje, na końcu "Install" → "Finish"
4. Sprawdzenie: otwórz Wiersz poleceń (Windows → wpisz `cmd` → Enter) i wpisz:
   ```
   git --version
   ```
   Powinieneś zobaczyć numer wersji (np. `git version 2.55.0.windows.3`)
5. Ustaw swoją tożsamość (potrzebne do commitów), podmieniając na swoje dane:
   ```
   git config --global user.name "Twoje Imie"
   git config --global user.email "twoj@email.com"
   ```

## 3. Konto GitHub i repozytorium projektu

1. Załóż konto na https://github.com (jeśli jeszcze nie masz)
2. Kliknij "+" (prawy górny róg) → "New repository"
3. Nazwa repozytorium: np. `moto-tracker`
4. Zaznacz "Add a README file"
5. Kliknij "Create repository"

## 4. Klonowanie repozytorium na komputer

1. Na stronie repozytorium kliknij zielony przycisk "Code", skopiuj adres (np. `https://github.com/twoj-login/moto-tracker.git`)
2. Otwórz Wiersz poleceń (cmd)
3. Przejdź do Pulpitu:
   ```
   cd Desktop
   ```
4. Sklonuj repozytorium:
   ```
   git clone https://github.com/twoj-login/moto-tracker.git
   ```

## 5. Instalacja esptool (narzędzie do wgrywania firmware na ESP32)

1. W Wierszu poleceń wpisz:
   ```
   pip install esptool
   ```
2. Uwaga: jeśli komenda `esptool.py` nie działa bezpośrednio (błąd "nie jest rozpoznawany"), wywołuj esptool przez Pythona:
   ```
   python -m esptool [dalsze argumenty]
   ```

## 6. Sprawdzenie portu COM płytki

1. Podłącz ESP32 do komputera kablem Type-C
2. Otwórz Menedżer urządzeń (Windows → "menedżer urządzeń" → Enter)
3. Rozwiń "Porty (COM i LPT)"
4. Zanotuj numer portu (np. `COM3`) — nazwa przy nim to zwykle "Silicon Labs CP210x" lub "USB-SERIAL CH340"

## 7. Pobranie firmware MicroPython

1. Wejdź na https://micropython.org/download/ESP32_GENERIC/
2. Pobierz najnowszy stabilny plik `.bin` z **głównej, generycznej** sekcji
3. Nazwa pliku będzie wyglądać mniej więcej tak: `ESP32_GENERIC-20260406-v1.28.0.bin`
4. Przenieś pobrany plik do folderu `moto-tracker` na Pulpicie

> **Ważne — sprawdzone doświadczeniem:** ESP32-WROOM-32S DevKit używa standardowego chipu (D0WD/D0WDQ6) — zawsze pobieraj zwykły "generic" firmware. **Nie pobieraj wariantu z dopiskiem "D2WD"** w nazwie — to firmware dla innego, rzadkiego chipu (ESP32-D2WD z wbudowaną pamięcią, bez zewnętrznej flash) i nie zadziała poprawnie na standardowej płytce DevKit, mimo że na pierwszy rzut oka nazwa wygląda podobnie.

## 8. Wymazanie i flashowanie ESP32

1. Otwórz Wiersz poleceń, przejdź do folderu projektu:
   ```
   cd Desktop\moto-tracker
   ```
2. Wymaż pamięć flash (zamień `COM3` na swój port):
   ```
   python -m esptool --port COM3 erase_flash
   ```
   - Jeśli terminal zawiesi się na "Connecting...", przytrzymaj przycisk **BOOT** na płytce, wciśnij i puść **EN/RST**, następnie puść **BOOT** — niektóre płytki wymagają ręcznego wejścia w tryb bootloadera
3. Po komunikacie "Flash memory erased successfully" wgraj firmware (zamień nazwę pliku, jeśli pobrałeś inną wersję):
   ```
   python -m esptool --port COM3 --baud 460800 write_flash 0x1000 ESP32_GENERIC-20260406-v1.28.0.bin
   ```
   - Jeśli znów zawiesi się na łączeniu, powtórz sekwencję z przyciskiem BOOT (płytka mogła się zresetować po poprzedniej operacji)
4. Poczekaj na "Hard resetting via RTS pin..." — to oznacza sukces

## 9. Pierwsze połączenie z Thonny

1. Otwórz Thonny
2. Kliknij nazwę interpretera w prawym dolnym rogu okna
3. Wybierz "MicroPython (ESP32)"
4. Wybierz odpowiedni port COM
5. W oknie Shell powinieneś zobaczyć baner z wersją MicroPythona i znak `>>>`

## 10. Instalacja sterownika sdcard.py (potrzebny do obsługi karty microSD)

1. Otwórz w przeglądarce: https://raw.githubusercontent.com/micropython/micropython-lib/master/micropython/drivers/storage/sdcard/sdcard.py
2. Zaznacz całą zawartość (Ctrl+A), skopiuj (Ctrl+C)
3. W Thonny: **File → New**, wklej zawartość
4. Zapisz (**Ctrl+S**) → wybierz **"MicroPython device"** (nie "This computer" — plik musi trafić na samą płytkę!)
5. Nazwa pliku: `sdcard.py`, zapisz w głównym katalogu (bez podfolderów)
6. (Opcjonalnie, dla porządku) zapisz też kopię lokalnie na komputerze w folderze `moto-tracker`, żeby dodać ją do repo

## 11. Potwierdzone piny podłączenia czujników

Te piny zostały zweryfikowane praktycznie (skanowaniem I2C, testami UART i SPI) na naszym zestawie — jeśli montujesz identyczny zestaw komponentów w ten sam sposób, powinny się zgadzać:

| Czujnik | Interfejs | Piny |
|---|---|---|
| MPU6050 (GY-521) | I2C | SDA=GPIO21, SCL=GPIO22 |
| GPS NEO-7M | UART | GPS TX → ESP32 GPIO16 (RX), GPS RX → ESP32 GPIO17 (TX) |
| Micro SD | SPI | CS=GPIO5, MOSI=GPIO23, CLK=GPIO18, MISO=GPIO19 |

Jeśli montujesz nowy zestaw od zera, zawsze warto zweryfikować to praktycznie zamiast zakładać — użyj skryptu skanującego I2C (dla MPU6050) i sprawdź fizycznie, gdzie prowadzą przewody GPS/SD, zamiast polegać wyłącznie na zdjęciu/opisie.

## 12. Test poszczególnych czujników (zalecana kolejność)

Zanim złożysz wszystko w jeden program, warto przetestować każdy element osobno w Thonny (kod w Shell lub jako zapisany plik `.py`):

1. **Dioda LED** (GPIO2) — najprostszy test, potwierdza że Thonny steruje płytką
2. **MPU6050** — skan I2C (`i2c.scan()`), potem odczyt akcelerometru/żyroskopu
3. **GPS** — odczyt surowych zdań NMEA przez UART; pamiętaj, że fix satelitarny wymaga kilkudziesięciu sekund i widoku nieba
4. **microSD** — montowanie, zapis, odczyt pliku testowego

> **Uwaga dotycząca kart SD:** jeśli natrafisz na uporczywy błąd `OSError: no SD card` mimo poprawnego okablowania (sprawdzonego multimetrem), sprawdzonego zasilania 3.3V i poprawnej biblioteki `sdcard.py` — to może być po prostu wadliwy egzemplarz modułu. W naszym przypadku dwa kolejne moduły SD okazały się wadliwe, dopiero trzeci zadziałał poprawnie. Jeśli masz pod ręką zapasowy moduł, warto go po prostu podmienić zamiast szukać dalej błędu w kodzie czy okablowaniu.

## 13. Uruchamianie programu automatycznie po starcie (bez laptopa)

MicroPython automatycznie uruchamia plik o nazwie **`main.py`**, jeśli jest zapisany bezpośrednio na płytce (nie na komputerze), zaraz po podłączeniu zasilania:

1. Otwórz gotowy skrypt logujący w Thonny
2. **File → Save As** → wybierz **"MicroPython device"**
3. Zapisz pod nazwą dokładnie **`main.py`**, w głównym katalogu

Od teraz płytka uruchomi logowanie samodzielnie po podłączeniu zasilania (np. z power banku), bez potrzeby podłączania laptopa.

## 14. Program logujący (main.py) — kluczowe wnioski

Poniższy szkielet łączy wszystkie trzy czujniki w jedną pętlę i zapisuje dane na kartę SD w formacie CSV (`timestamp_ms,accel_x,accel_y,accel_z,gyro_x,gyro_y,gyro_z,lat,lon,gps_valid`). Dwie rzeczy w nim są krytyczne i wynikają wprost z problemów, na jakie trafiliśmy w testach:

1. **Unikalne nazwy plików** — jeśli nazwiesz plik na podstawie `time.ticks_ms()` (czas od uruchomienia płytki), przy kolejnych uruchomieniach ten licznik bywa bardzo podobny, co prowadzi do **nadpisania poprzedniego loga** bez ostrzeżenia. Zamiast tego sprawdzamy przy starcie, jakie numery plików już są zajęte na karcie, i bierzemy kolejny wolny.
2. **Odporność na błędy (`try/except`)** — bez tego pojedynczy nieoczekiwany błąd (np. zakłócona linijka NMEA z GPS) potrafi zatrzymać całą pętlę na stałe, kończąc logowanie po kilkudziesięciu sekundach zamiast po godzinach. Błędy zapisujemy do osobnego `errors.log`, żeby móc je zdiagnozować później, ale **nie przerywamy** głównej pętli.

```python
from machine import Pin, SPI, I2C, UART
import os
import sdcard
import time

# --- MPU6050 (I2C) ---
MPU_ADDR = 0x68
i2c = I2C(0, sda=Pin(21), scl=Pin(22), freq=100000)
i2c.writeto_mem(MPU_ADDR, 0x6B, b'\x00')

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
    try:
        if gps_uart.any():
            gps_buffer += gps_uart.read()
            while b"\n" in gps_buffer:
                line, gps_buffer = gps_buffer.split(b"\n", 1)
                try:
                    line = line.decode("ascii", "ignore").strip()
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
                except Exception:
                    pass  # pojedyncza uszkodzona linijka NMEA - pomijamy
    except Exception:
        pass  # blad na poziomie UART - rowniez pomijamy

# --- SD (SPI) ---
spi = SPI(1, baudrate=1000000, sck=Pin(18), mosi=Pin(23), miso=Pin(19))
cs = Pin(5)
sd = sdcard.SDCard(spi, cs)
os.mount(sd, "/sd")

# unikalna nazwa pliku - sprawdzamy jaki numer jest juz zajety
existing = os.listdir("/sd")
next_num = 1
while "log_{:04d}.csv".format(next_num) in existing:
    next_num += 1
log_filename = "/sd/log_{:04d}.csv".format(next_num)

with open(log_filename, "w") as f:
    f.write("timestamp_ms,accel_x,accel_y,accel_z,gyro_x,gyro_y,gyro_z,lat,lon,gps_valid\n")

print("Logowanie do pliku:", log_filename)

buffer = []
BUFFER_FLUSH_SIZE = 20   # zapis na SD co ok. 2 sekundy przy 10Hz
SAMPLE_INTERVAL_MS = 100  # 10 odczytow na sekunde

last_sample_time = time.ticks_ms()

while True:
    try:
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
                buffer = []

        update_gps()
    except Exception as e:
        try:
            with open("/sd/errors.log", "a") as ef:
                ef.write("{}: {}\n".format(time.ticks_ms(), str(e)))
        except Exception:
            pass
        time.sleep_ms(100)
```

Zapisz jako `main.py` na **"MicroPython device"** (żeby uruchamiało się automatycznie po podłączeniu zasilania), i tak samo lokalnie w folderze projektu do repo.

## 15. Odczyt logów z karty SD po teście

Przy odczycie plików na ESP32 **nigdy nie używaj `f.readlines()` na dużym pliku** — to próbuje wczytać cały plik do pamięci RAM naraz, a ESP32 ma jej bardzo mało; przy dłuższych logach (tysiące wierszy) skończy się to błędem `MemoryError`. Zamiast tego czytaj plik linijka po linijce w pętli `for line in f:`:

```python
from machine import Pin, SPI
import os, sdcard

spi = SPI(1, baudrate=1000000, sck=Pin(18), mosi=Pin(23), miso=Pin(19))
cs = Pin(5)
sd = sdcard.SDCard(spi, cs)
os.mount(sd, "/sd")
print(os.listdir("/sd"))

def count_and_peek(filename):
    count = 0
    first_line = None
    last_line = None
    with open("/sd/" + filename) as f:
        for line in f:
            count += 1
            if count == 2:
                first_line = line.strip()
            last_line = line.strip()
    print(filename, "-> wierszy:", count)
    if first_line:
        print("   pierwszy:", first_line)
    if last_line:
        print("   ostatni: ", last_line)
```

Praktyczniejsza opcja przy większej ilości danych: wyjmij samą kartę SD z modułu i odczytaj ją bezpośrednio czytnikiem w komputerze — dużo szybsze niż odczyt przez wolne połączenie szeregowe ESP32↔Thonny.

> **Uwaga:** podłączenie płytki do komputera przez Thonny samo w sobie wykonuje reset (soft reboot), co automatycznie uruchamia `main.py` na nowo — może to stworzyć dodatkowy, bardzo krótki plik logu. To normalne zachowanie, nie błąd.

## 16. Wnioski z testów w terenie

- **Antena GPS potrzebuje swobodnego widoku nieba, skierowana ku górze.** Test, w którym moduł leżał przy plecach/biodrze pod ubraniem, nie złapał namiaru przez cały ~50-sekundowy test mimo bycia na zewnątrz. Test z anteną leżącą płasko, skierowaną w niebo (na balkonie) złapał i utrzymał stabilny fix przez cały ~17-minutowy przebieg.
- **Tanie power banki mogą wyłączać się automatycznie przy zbyt niskim poborze prądu** — układ ESP32+czujniki pobiera niewiele energii, więc warto to mieć na uwadze przy dłuższych testach/projektowaniu zasilania docelowego.

## 17. Praca z Gitem — zapisywanie postępu

Po każdym większym kroku (nowy działający skrypt, ważna poprawka):

```
cd Desktop\moto-tracker
git add nazwa_pliku.py
git commit -m "Krotki opis co zrobiono"
git push
```

---

Po wykonaniu tych kroków płytka jest gotowa do rejestrowania danych z jazdy (GPS + IMU) na kartę SD.
