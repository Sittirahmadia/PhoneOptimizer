# 📱 Phone Optimizer — Cara Build APK

## Persyaratan
- Linux / WSL2 / macOS (Windows pakai WSL)
- Python 3.10+
- buildozer

---

## 1. Install Buildozer

```bash
pip install buildozer
# Install dependensi sistem (Ubuntu/Debian):
sudo apt update && sudo apt install -y \
  git zip unzip openjdk-17-jdk python3-pip \
  python3-venv autoconf libtool pkg-config \
  zlib1g-dev libncurses5-dev libncursesw5-dev \
  libtinfo5 cmake libffi-dev libssl-dev
```

---

## 2. Build APK

```bash
cd PhoneOptimizer/
buildozer android debug
```

APK akan ada di folder `bin/` setelah build selesai (~15-30 menit pertama kali).

---

## 3. Install ke HP

```bash
adb install bin/phoneoptimizer-1.0-armeabi-v7a-debug.apk
```

Atau copy APK ke HP dan install manual.

---

## 4. Grant Izin WRITE_SECURE_SETTINGS (PENTING!)

Fitur **animasi**, **AOD**, dan **battery saver** butuh izin ini.
Jalankan **sekali** setelah install:

```bash
adb shell pm grant org.optimizer.phoneoptimizer android.permission.WRITE_SECURE_SETTINGS
```

Setelah itu, cabut USB — app sudah bisa dipakai mandiri.

---

## 5. Izin WRITE_SETTINGS

Saat pertama buka app, akan muncul popup minta izin **Modify System Settings**.
Ketuk banner kuning di bagian atas → aktifkan dari Settings → izin granted.

---

## Fitur Aplikasi

| Fitur | Butuh Izin |
|-------|-----------|
| Lock 120Hz | WRITE_SETTINGS |
| Matikan Auto Brightness | WRITE_SETTINGS |
| Pointer Speed | WRITE_SETTINGS |
| Haptic on/off | WRITE_SETTINGS |
| Animasi UI | WRITE_SECURE_SETTINGS (ADB) |
| Matikan AOD | WRITE_SECURE_SETTINGS (ADB) |
| Matikan Battery Saver | WRITE_SECURE_SETTINGS (ADB) |

---

## Catatan
- Tidak butuh root sama sekali
- WRITE_SECURE_SETTINGS cukup di-grant sekali via ADB
- Ditest di Android 12+
