#!/bin/bash

# Render Deploy Helper Script
# Bu skript lokal muhitda Render konfiguratsiyasini testlash uchun

echo "🔧 Render Deploy Tayyorgarlik..."

# 1. Environment variables faylini yaratish
if [ ! -f .env.render ]; then
    echo "📝 .env.render faylini yaratish..."
    cat > .env.render <<EOF
DEBUG=False
SECRET_KEY=$(python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
ALLOWED_HOSTS=*,.render.com,.onrender.com
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
DATABASE_URL=sqlite:///db.sqlite3
EOF
    echo "✅ .env.render yaratildi"
else
    echo "⚠️  .env.render allaqachon mavjud"
fi

# 2. Virtual environment yaratish (agar yo'q bo'lsa)
if [ ! -d venv ]; then
    echo "🐍 Virtual environment yaratish..."
    python -m venv venv
    echo "✅ Virtual environment yaratildi"
else
    echo "✅ Virtual environment mavjud"
fi

# 3. Kutubxonalarni o'rnatish
echo "📦 Kutubxonalarni yangilash..."
source venv/bin/activate
pip install -r requirements.txt
echo "✅ Kutubxonalarni o'rnatildi"

# 4. Static fayllarni to'plash
echo "📁 Static fayllarni to'plash..."
python manage.py collectstatic --noinput
echo "✅ Static fayllar to'plandi"

# 5. Migrations
echo "🔄 Database migrations..."
python manage.py migrate
echo "✅ Migrations bajarildi"

echo ""
echo "🎉 Tayyor! Keyingi qadamlar:"
echo "1. .env.render faylini tahrirlang (Telegram token va chat ID qo'shing)"
echo "2. git push qiling: git add . && git commit -m 'Render deploy prep' && git push"
echo "3. Render'da web service yarating"
echo ""
echo "Yordam: RENDER_DEPLOY_GUIDE.md faylini o'qing"
