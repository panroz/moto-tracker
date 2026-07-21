# Instrukcja: konfiguracja ESP32 od zera (moto-tracker)

Ta instrukcja zakłada nowy komputer z systemem Windows, na którym nic jeszcze nie jest zainstalowane, oraz świeżo rozpakowaną płytkę ESP32-WROOM-32S DevKit z podłączonymi czujnikami (MPU6050, GPS NEO-7M, moduł microSD).

## Czego będziesz potrzebować
- Komputer z Windows
- Kabel USB Type-C
- Płytka ESP32-WROOM-32S DevKit z podłączonymi czujnikami
- Konto na GitHub (https://github.com)

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

## 14. Praca z Gitem — zapisywanie postępu

Po każdym większym kroku (nowy działający skrypt, ważna poprawka):

```
cd Desktop\moto-tracker
git add nazwa_pliku.py
git commit -m "Krotki opis co zrobiono"
git push
```

---

Po wykonaniu tych kroków płytka jest gotowa do rejestrowania danych z jazdy (GPS + IMU) na kartę SD.
