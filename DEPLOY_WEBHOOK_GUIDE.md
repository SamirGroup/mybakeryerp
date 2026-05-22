# Railway Deploy Webhook Sozlamalari

## Railway'da Avtomatik Deploy

Railway GitHub'ga ulangandan keyin avtomatik deploy qiladi. Lekin agar xatolik bo'lsa, quyidagilarni tekshiring:

### 1. Railway Dashboard'da Tekshirish

1. [Railway.app](https://railway.app) ga kiring
2. Loyihangizni tanlang
3. "Deployments" bo'limiga o'ting

### 2. Logs ni Tekshirish

Agar deploy xato bo'lsa:
- Deployments → "View Logs" ni bosing
- Xatolik xabarini o'qing
- Odatda quyidagi xatolar bo'ladi:

#### Xato: SECRET_KEY yo'q
```
Environment variable 'SECRET_KEY' not found
```
**Yechim:** Railway → Variables → SECRET_KEY qo'shing

#### Xato: DATABASE_URL yo'q
```
Environment variable 'DATABASE_URL' not found
```
**Yechim:** Railway → New → Database → PostgreSQL → Connection URL ni oling va Variables ga qo'shing

#### Xato: Telegram token noto'g'ri
```
Telegram bot token invalid
```
**Yechim:** @BotFather'dan yangi token oling va TELEGRAM_BOT_TOKEN ni yangilang

### 3. Manual Deploy

Agar avtomatik deploy ishlamasa:

```bash
# Railway CLI orqali
railway login
railway link
railway run python manage.py migrate
railway run python manage.py collectstatic --noinput
```

### 4. GitHub Webhook Qayta Ishga Tushirish

Agar GitHub'dan push qilingan bo'lsangiz, lekin Railway deploy qilmagan bo'lsa:

1. Railway dashboard → Settings → "Deployments" 
2. "Manual Deploy" → "Deploy Latest Commit"
3. Yoki GitHub'da yana bir marta `git push` qiling

---

## Render Deploy Webhook

Render'da avtomatik deploy GitHub'dan keyin avtomatik ishlaydi.

### Tekshirish

1. [Render Dashboard](https://dashboard.render.com)
2. Web Service ni tanlang
3. "Events" bo'limida deploy log'larni ko'ring

### Manual Deploy

1. "Manual Deploy" → "Deploy Newest Commit"
2. Yoki:
```bash
# Render CLI
render down
render up
```

---

## Face ID Daemon Ishga Tushirish

Railway/Render'da Face ID daemonni ishga tushirish uchun:

### Railway

```bash
# Railway CLI
railway run python manage.py face_id_daemon
```

### Render

Render'da "Workers" bo'limida yangi service yarating:
- Build Command: `pip install -r requirements.txt`
- Start Command: `python manage.py face_id_daemon`

---

## Telegram Bot Doimiy Ishlash

Telegram bot endi "Doimiy ulanish" sozlamasi bilan faol:

1. Admin panel → Telegram Sozlamalar
2. "Doimiy ulanish" tugmasini belgilang
3. Saqlang

Bot har doim xabarlarni yuborishga tayyor bo'ladi.

---

## Sotuv Formasi Scroll Muammosi

Endi tuzatildi! Sotuv tasdiqlash formasi `sticky` holatda, scroll bo'lsa ham ko'rinadi.

---

## Yordam

Agar xatolik bo'lsa:
1. Railway/Render log'larni tekshiring
2. GitHub'da issue oching
3. `python manage.py check` ni lokal'da ishga tushiring
