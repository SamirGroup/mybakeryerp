# Face ID Tizimi - O'rnatish va Sozlash Qo'llanmasi

## 1. Tavsiya Qilingan Face ID Qurilmalar

### A) Arzon Variantlar (Budget):
- **Raspberry Pi 4 + USB Webcam** (Logitech C920/C922)
  - Narxi: ~$150-200
  - Face ID uchun yetarli
  - O'rnatish oson

- **Intel RealSense D415/D435**
  - Narxi: ~$200-300
  - 3D depth sensor bilan
  - Aniqroq tanishish

### B) O'rta Variant:
- **AWS DeepLens**
  - Narxi: ~$250
  - AWS integratsiyasi
  - Machine Learning qo'llab-quvvatlaydi

- **NVIDIA Jetson Nano + Camera**
  - Narxi: ~$200-300
  - AI uchun optimallashtirilgan
  - Yuqori tezlik

### C) Professional Variant:
- **Face ID Kiosk (Ready-made)**
  - Narxi: $500-1000
  - Tayyor yechim
  - Minimal sozlash

### D) Windows PC uchun eng yaxshi variant:
- **Logitech C920/C922 HD Pro Webcam**
  - Narxi: ~$80-120
  - 1080p video sifat
  - Avtofokus
  - Windows/Linux/Mac bilan ishlaydi
  - **TAVSIYA ETILADI**

- **Microsoft LifeCam Studio**
  - Narxi: ~$70-100
  - 1080p HD sensor
  - TrueColor texnologiyasi

## 2. Driver va Kutubxonalarni O'rnatish

### Windows:
```bash
# 1. Python va pip yangilash
python -m pip install --upgrade pip

# 2. Asosiy kutubxonalarni o'rnatish
pip install -r requirements_face_id.txt

# 3. dlib uchun C++ compiler (Windows)
# Visual Studio Build Tools o'rnatish: https://visualstudio.microsoft.com/visual-cpp-build-tools/
# Yoki CMake o'rnatish: pip install cmake

# 4. OpenCV test
python -c "import cv2; print('OpenCV versiyasi:', cv2.__version__)"

# 5. Face recognition test
python -c "import face_recognition; print('Face recognition tayyor!')"
```

### Linux (Ubuntu/Debian):
```bash
# Tizim paketlarini yangilash
sudo apt-get update
sudo apt-get install -y cmake libopenblas-dev liblapack-dev libjpeg-dev

# Python kutubxonalar
pip install -r requirements_face_id.txt

# Kamera test
sudo apt-get install v4l-utils
v4l2-ctl --list-devices
```

## 3. Face ID Kamera Sozlash

### A) Hardware ulash:
1. Kamerani USB portga ulang
2. Windows: Driver avtomatik o'rnatiladi
3. Linux: `sudo apt-get install v4l-utils`

### B) Test qilish:
```python
import cv2

# Kamera ochish
cap = cv2.VideoCapture(0)

# Test kadrlar
ret, frame = cap.read()
if ret:
    print("✅ Kamera ishlayapti!")
    cv2.imwrite('test.jpg', frame)
else:
    print("❌ Kamera topilmadi!")

cap.release()
```

## 4. Tizimga Ulash va Avtomatik Ishga Tushirish

### Django management command orqali:
```bash
# Terminal 1: Django server
python manage.py runserver 8800

# Terminal 2: Face ID monitoring (avtomatik)
python manage.py start_face_id

# Boshqa kamera bilan (agar birinchi kamera band bo'lsa)
python manage.py start_face_id --camera 1

# Ishonchlilik darajasini o'zgartirish (default: 0.6)
python manage.py start_face_id --confidence 0.5
```

### Windows Task Scheduler orqali avtomatik ishga tushirish:
1. Task Scheduler oching
2. "Create Basic Task" ni tanlang
3. "start_face_id.bat" faylini ishga tushirish

```batch
@echo off
cd C:\path\to\project
python manage.py start_face_id
```

### Systemd (Linux):
```ini
# /etc/systemd/system/face-id.service
[Unit]
Description=Face ID Monitoring
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/project
ExecStart=/usr/bin/python3 manage.py start_face_id
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable face-id
sudo systemctl start face-id
```

## 5. POS Printer Integratsiyasi

### Tavsiya Qilingan Mini Printerlar:
- **Epson TM-T20II** - $300-400
- **Star TSP143III** - $200-300
- **Bixolon BTP-R490** - $150-250
- **Xprinter XP-58** - $80-120 (Budget)
- **Xprinter XP-80** - $100-150 (80mm, tavsiya etiladi)

### Driver O'rnatish:
1. Printerni USB yoki Ethernet orqali ulang
2. Windows: Printer & Scanners → Add Printer
3. Test chop qiling

### Chek chop etish:
Tizim avtomatik ravishda HTML chek yaratadi va brauzer orqali pechat qilish imkonini beradi.
Sotuv tugagach, "Chekni pechat qilish" tugmasi bosiladi.

## 6. Xavfsizlik

- Kamera ma'lumotlarini shifrlang
- Face ID ma'lumotlarini maxfiy saqlang
- Access log'larni yozing
- Regular backup oling

## 7. Troubleshooting

### Kamera ishlamayapti:
```bash
# Linux
v4l2-ctl --list-devices

# Test
ffplay /dev/video0
```

### Face recognition sekin:
- Camera resolution kamaytiring (640x480)
- Recognition frequency kamaytiring (har 5-kadr)
- GPU qo'llab-quvvatlash yoqilsin

### dlib o'rnatilmayapti:
```bash
# Windows
pip install cmake
pip install dlib

# Agar xato bersa
conda install -c conda-forge dlib
```

---
**Qo'shimcha savollar bo'lsa, yozing! 🚀**
