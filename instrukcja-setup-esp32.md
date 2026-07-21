# Instrukcja: konfiguracja ESP32 od zera (moto-tracker)

Ta instrukcja zakłada nowy komputer z systemem Windows, na którym nic jeszcze nie jest zainstalowane, oraz świeżo rozpakowaną płytkę ESP32-WROOM-32S DevKit.

## Czego będziesz potrzebować
- Komputer z Windows
- Kabel USB Type-C
- Płytka ESP32-WROOM-32S DevKit
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

## 3. Konto GitHub i repozytorium projektu

1. Załóż konto na https://github.com (jeśli jeszcze nie masz)
2. Kliknij "+" (prawy górny róg) → "New repository"
3. Nazwa repozytorium: `moto-tracker`
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

## 6. Sprawdzenie portu COM płytki

1. Podłącz ESP32 do komputera kablem Type-C
2. Otwórz Menedżer urządzeń (Windows → "menedżer urządzeń" → Enter)
3. Rozwiń "Porty (COM i LPT)"
4. Zanotuj numer portu (np. `COM3`) — nazwa przy nim to zwykle "Silicon Labs CP210x" lub "USB-SERIAL CH340"

## 7. Pobranie firmware MicroPython

1. Wejdź na https://micropython.org/download/ESP32_GENERIC/
2. Pobierz najnowszy stabilny plik `.bin` z **głównej, generycznej** sekcji (bez dopisków typu "D2WD", "SPIRAM", "unicore" w nazwie — te są przeznaczone dla innych, specyficznych chipów)
3. Nazwa pliku będzie wyglądać mniej więcej tak: `ESP32_GENERIC-20260406-v1.28.0.bin`
4. Przenieś pobrany plik do folderu `moto-tracker` na Pulpicie

> **Ważne:** ESP32-WROOM-32S DevKit używa standardowego chipu (D0WD/D0WDQ6) — zawsze pobieraj zwykły "generic" firmware, nie warianty specjalne.

## 8. Wymazanie i flashowanie ESP32

1. Otwórz Wiersz poleceń, przejdź do folderu projektu:
   ```
   cd Desktop\moto-tracker
   ```
2. Wymaż pamięć flash (zamień `COM3` na swój port):
   ```
   python -m esptool --port COM3 erase_flash
   ```
   - Jeśli terminal zawiesi się na "Connecting...", przytrzymaj przycisk **BOOT** na płytce, wciśnij i puść **EN/RST**, następnie puść **BOOT**
3. Po komunikacie "Flash memory erased successfully" wgraj firmware (zamień nazwę pliku, jeśli pobrałeś inną wersję):
   ```
   python -m esptool --port COM3 --baud 460800 write_flash 0x1000 ESP32_GENERIC-20260406-v1.28.0.bin
   ```
   - Jeśli znów zawiesi się na łączeniu, powtórz sekwencję z przyciskiem BOOT
4. Poczekaj na "Hard resetting via RTS pin..." — to oznacza sukces

## 9. Pierwsze połączenie z Thonny

1. Otwórz Thonny
2. Kliknij nazwę interpretera w prawym dolnym rogu okna
3. Wybierz "MicroPython (ESP32)"
4. Wybierz odpowiedni port COM
5. W oknie Shell powinieneś zobaczyć baner z wersją MicroPythona i znak `>>>`

## 10. Zapisanie postępu w Gicie

1. W Wierszu poleceń, w folderze projektu:
   ```
   git add ESP32_GENERIC-20260406-v1.28.0.bin
   git commit -m "Dodano firmware MicroPython uzywany do flashowania ESP32"
   git push
   ```

---

Po wykonaniu tych kroków płytka jest gotowa do pisania i wgrywania kodu w MicroPythonie przez Thonny.
