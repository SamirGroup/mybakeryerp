# Railway va Render Deploy Qo'llanmasi

## 🚀 Railway Deploy

### 1. Railway'da yangi Project yaratish
1. [Railway.app](https://railway.app) ga kiring
2. "New Project" → "Deploy from GitHub repo"
3. `novvoyxona-proekt` repozitoriyasini tanlang

### 2. Environment Variables sozlash
Railway dashboard'da quyidagi variables qo'shing:

```env
SECRET_KEY=your-secret-key-here (random string)
DEBUG=False
ALLOWED_HOSTS=your-app.railway.app,localhost,127.0.0.1
DATABASE_URL=your-postgresql-url
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_CHAT_ID=your-chat-id
```

### 3. PostgreSQL Database ulash
1. Railway dashboard'da "New" → "Database" → "PostgreSQL"
2. Database ulanish URL'ini oling va `DATABASE_URL` ga qo'ying

### 4. Deploy
Railway avtomatik deploy qiladi. Agar xato bo'lsa:
- "Deployments" → "View Logs" ni tekshiring
- O'zbek tilidagi xatoliklarni to'g'rilang

### 5. Migrations va Collectstatic
Deploydan keyin Railway avtomatik ishlaydi, lekin qo'lda ham bajarish mumkin:

```bash
# Railway CLI orqali
railway run python manage.py migrate
railway run python manage.py collectstatic --noinput
railway run python manage.py createsuperuser
```

---

## 🎨 Render Deploy

### 1. Render'da yangi Web Service yaratish
1. [render.com](https://render.com) ga kiring
2. "New" → "Web Service"
3. GitHub repozitoriyani tanlang

### 2. Build va Start Commands
```
Build Command: pip install -r requirements.txt
Start Command: gunicorn bakery_erp.wsgi:application --bind 0.0.0.0:$PORT
```

### 3. Environment Variables
Render dashboard'da qo'shing:

```env
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-app.onrender.com,testserver
DATABASE_URL=your-postgresql-url
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_CHAT_ID=your-chat-id
```

### 4. PostgreSQL Database
1. "New" → "PostgreSQL"
2. Connection URL'ni olib, `DATABASE_URL` ga qo'ying

### 5. Auto-deploy
Render har safar `git push` qilinganda avtomatik deploy qiladi.

### 6. Migrations
Render'da "Shell" orqali yoki Webhook qo'shing:

```bash
# Render Shell'da
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

---

## 🔧 Muhim Sozlamalar

### Telegram Bot Doimiy Ishlash
1. Admin panel → Telegram Sozlamalar
2. "Doimiy ulanish" tugmasini belgilang
3. Bot har doim xabarlarni yuborishga tayyor bo'ladi

### Face ID Kamera
1. Face ID Boshqaruvi sahifasiga o'ting (`/face-id/cameras/`)
2. Kamerani qo'shing va "Asosiy" qilib belgilang
3. "Monitoringni Boshlash" tugmasini bosing

### Sotuv Formasi Scroll Muammosi Tuzatildi
Sotuv tasdiqlash formasi endi `sticky` holatda, scroll bo'lsa ham ko'rinadi.

---

## 🐛 Xatolarni Tekshirish

### 1. Token Xatolari
Telegram bot token xato bo'lsa:
- `@BotFather` orqali yangi token oling
- Railway/Render'da `TELEGRAM_BOT_TOKEN` ni yangilang
- Admin panel → Telegram Sozlamalar → Saqlash

### 2. Database Xatolari
```bash
# Local'da test
python manage.py migrate
python manage.py flush  # Agar kerak bo'lsa
```

### 3. Static Files
```bash
python manage.py collectstatic --noinput
```

---

## ✅ Deploy Checklist

- [ ] `DEBUG=False` qiling
- [ ] `SECRET_KEY` ni o'zgartiring
- [ ] `ALLOWED_HOSTS` ni to'g'rilang
- [ ] PostgreSQL database ulang
- [ ] Migrations ishga tushiring
- [ ] Static files yig'ing
- [ ] Superuser yarating
- [ ] Telegram bot sozlamalarini kiritib, "Doimiy ulanish"ni belgilang
- [ ] Face ID kamerani sozlang
- [ ] Test sotuv yarating
- [ ] Scroll muammosini tekshiring (sotuv formasi doim ko'rinadi)

---

## 📞 Yordam

Agar xatolik bo'lsa:
1. Railway/Render log'larni tekshiring
2. `python manage.py check` ishga tushiring
3. GitHub issues'da savol bering
