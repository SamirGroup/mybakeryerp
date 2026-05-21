# Bakery ERP — Render Deploy Qo'llanmasi

## 📋 Deploydan Oldin Tekshirish

### 1. Git Repository
Loyihangiz GitHub/GitLab/Bitbucket repositoryda bo'lishi kerak:
```bash
git init
git add .
git commit -m "Initial commit for Render deploy"
git branch -M main
git remote add origin <repository-url>
git push -u origin main
```

### 2. Muhim Fayllar
Quyidagi fayllar repositoryda bo'lishi kerak:
- ✅ `render.yaml` — Render konfiguratsiyasi
- ✅ `requirements.txt` — Python kutubxonalari
- ✅ `Procfile` — Gunicorn start buyrug'i
- ✅ `manage.py` — Django CLI
- ✅ `bakery_erp/settings.py` — Sozlamalar

## 🚀 Render'da Deploy Qilish

### Qadam 1: Render Akkaunti Yarating
1. [render.com](https://render.com) ga kiring
2. GitHub/GitLab orqali kirish qiling
3. "New +" → "Web Service" ni tanlang

### Qadam 2: Repositoryni Ulash
- **Repository**: Loyihangiz repositoryni tanlang
- **Name**: `bakery-erp` (yoki istalgan nom)
- **Region**: Oregon (yoki sizga yaqin)
- **Branch**: `main`
- **Runtime**: `Python`
- **Build Command**: `pip install -r requirements.txt && python manage.py collectstatic --noinput`
- **Start Command**: `gunicorn bakery_erp.wsgi:application --log-file -`

### Qadam 3: Environment Variables Sozlash
Render dashboard'da "Environment" bo'limida quyidagilarni qo'shing:

| Key | Value |
|-----|-------|
| `DEBUG` | `False` |
| `SECRET_KEY` | `openssl rand -base64 64` (terminalda generatsiya qiling) |
| `ALLOWED_HOSTS` | `*` (yoki `yourdomain.com`) |
| `TELEGRAM_BOT_TOKEN` | O'zingizning bot tokeningiz |
| `TELEGRAM_CHAT_ID` | O'zingizning chat ID'ingiz |
| `DATABASE_URL` | Render avtomatik yaratadi (PostgreSQL) |

**SECRET_KEY generatsiya qilish:**
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### Qadam 4: Database Qo'shish
1. "Databases" → "New Database" → "PostgreSQL"
2. Nom: `bakery-db`
3. Plan: **Free** (750 soat/moy)
4. Database URL avtomatik environment variable sifatida qo'shiladi

### Qadam 5: Deploy
- "Create Web Service" ni bosing
- Build va deploy avtomatik boshlanadi (~3-5 daqiqa)
- Loglarni monitoring qiling

## 🔧 Deploydan Keyin

### 1. Database Migrations
Render dashboard'da "Shell" ga kiring va:
```bash
python manage.py migrate
```

### 2. Superuser Yarating
```bash
python manage.py createsuperuser
```
- Username, email, parol kiriting

### 3. Static Fayllar
Build command avtomatik `collectstatic` ishga tushiradi. Agar muammo bo'lsa:
```bash
python manage.py collectstatic --noinput
```

### 4. Admin Panelga Kirish
```
https://your-app-name.onrender.com/admin/
```

## ⚠️ Muammolarni Hal Qilish

### Build Muvaffaqiyatsiz
- `requirements.txt` to'g'riligini tekshiring
- Build loglarni ko'ring
- Python versiyasi `runtime.txt` da `python-3.12.7`

### Database Xatolik
- `DATABASE_URL` environment variable borligini tekshiring
- `dj-database-url` va `psycopg2-binary` requirements.txt da

### Static Fayllar Ko'rinmayapti
- `WHITENOISE` to'g'ri konfiguratsiya qilingan
- `STATIC_ROOT` sozlamasi to'g'ri

### 502 Bad Gateway
- Start command to'g'ri: `gunicorn bakery_erp.wsgi:application --log-file -`
- `bakery_erp/wsgi.py` mavjud

## 🌐 Custom Domain (Ixtiyoriy)
1. "Settings" → "Custom Domain"
2. Domin nomini kiriting
3. DNS sozlamalarini yangilang
4. SSL avtomatik

## 💡 Free Plan Cheklovlari
- **750 soat/moy** (oyiga ~25 kun)
- **Auto-sleep**: 15 daqiqa faolsizlikdan keyin uyquga ketadi
- **Birinchi so'rovda 30-50 soniya** uyqudan turish
- **PostgreSQL**: 1 GB storage, 1000 connections

## 🔄 Yangilash Deploy
```bash
git add .
git commit -m "Update description"
git push origin main
```
Render avtomatik rebuild va deploy qiladi (~2-3 daqiqa).

## 📊 Monitoring
- **Logs**: Dashboard'da "Logs" bo'limi
- **Metrics**: CPU, Memory, Request count
- **Uptime**: 99% ga yaqin (free plan)

---
**Muammo bo'lsa**: Render loglarini tekshiring va environment variables to'g'riligini tasdiqlang.
