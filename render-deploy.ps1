# Render Deploy Helper Script (PowerShell)
# Windows uchun

Write-Host "🔧 Render Deploy Tayyorgarlik..." -ForegroundColor Cyan

# 1. Environment variables faylini yaratish
if (-not (Test-Path .env.render)) {
    Write-Host "📝 .env.render faylini yaratish..." -ForegroundColor Yellow
    
    $secretKey = python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
    
    @"
DEBUG=False
SECRET_KEY=$secretKey
ALLOWED_HOSTS=*,.render.com,.onrender.com
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
DATABASE_URL=sqlite:///db.sqlite3
"@ | Out-File -FilePath .env.render -Encoding utf8
    
    Write-Host "✅ .env.render yaratildi" -ForegroundColor Green
} else {
    Write-Host "⚠️  .env.render allaqachon mavjud" -ForegroundColor Yellow
}

# 2. Virtual environment yaratish (agar yo'q bo'lsa)
if (-not (Test-Path venv)) {
    Write-Host "🐍 Virtual environment yaratish..." -ForegroundColor Yellow
    python -m venv venv
    Write-Host "✅ Virtual environment yaratildi" -ForegroundColor Green
} else {
    Write-Host "✅ Virtual environment mavjud" -ForegroundColor Green
}

# 3. Kutubxonalarni o'rnatish
Write-Host "📦 Kutubxonalarni yangilash..." -ForegroundColor Yellow
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
Write-Host "✅ Kutubxonalarni o'rnatildi" -ForegroundColor Green

# 4. Static fayllarni to'plash
Write-Host "📁 Static fayllarni to'plash..." -ForegroundColor Yellow
python manage.py collectstatic --noinput
Write-Host "✅ Static fayllar to'plandi" -ForegroundColor Green

# 5. Migrations
Write-Host "🔄 Database migrations..." -ForegroundColor Yellow
python manage.py migrate
Write-Host "✅ Migrations bajarildi" -ForegroundColor Green

Write-Host ""
Write-Host "🎉 Tayyor! Keyingi qadamlar:" -ForegroundColor Green
Write-Host "1. .env.render faylini tahrirlang (Telegram token va chat ID qo'shing)"
Write-Host "2. git push qiling: git add . && git commit -m 'Render deploy prep' && git push"
Write-Host "3. Render'da web service yarating"
Write-Host ""
Write-Host "Yordam: RENDER_DEPLOY_GUIDE.md faylini o'qing" -ForegroundColor Cyan
