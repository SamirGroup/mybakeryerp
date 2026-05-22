from django.db import models
from django.contrib.auth.models import User


class TelegramSettings(models.Model):
    """Telegram bot sozlamalari — yagona qator (singleton)."""
    bot_token = models.CharField(max_length=200, blank=True, verbose_name="Bot Token")
    chat_id   = models.CharField(max_length=50, blank=True, verbose_name="Chat ID")
    is_active = models.BooleanField(default=True, verbose_name="Faol")
    is_persistent = models.BooleanField(default=True, verbose_name="Doimiy ulanish")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Telegram Sozlamalari"

    def __str__(self):
        return f"Telegram Bot {'✅' if self.is_active and self.bot_token else '❌'}"

    @classmethod
    def get(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class BranchTelegramSettings(models.Model):
    """Har bir filial uchun alohida Telegram sozlamalari."""
    branch    = models.OneToOneField(
        'branches.Branch', on_delete=models.CASCADE,
        related_name='telegram_settings', verbose_name="Filial"
    )
    bot_token = models.CharField(max_length=200, blank=True, verbose_name="Bot Token")
    chat_id   = models.CharField(max_length=50, blank=True, verbose_name="Chat ID")
    is_active = models.BooleanField(default=True, verbose_name="Faol")
    is_persistent = models.BooleanField(default=True, verbose_name="Doimiy ulanish")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Filial Telegram Sozlamalari"

    def __str__(self):
        return f"{self.branch.name} Telegram {'✅' if self.is_active and self.bot_token else '❌'}"

    @classmethod
    def get_for_branch(cls, branch):
        obj, _ = cls.objects.get_or_create(branch=branch)
        return obj


class UserProfile(models.Model):
    user        = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    branch      = models.ForeignKey(
        'branches.Branch', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='admins'
    )
    first_name  = models.CharField(max_length=100, blank=True)
    last_name   = models.CharField(max_length=100, blank=True)
    phone       = models.CharField(max_length=30, blank=True)
    address     = models.TextField(blank=True)

    def __str__(self):
        full = f"{self.first_name} {self.last_name}".strip()
        return full or self.user.username

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.user.username


class CameraDevice(models.Model):
    """Face ID uchun kamera qurilmalari"""
    name = models.CharField(max_length=200, verbose_name="Kamera nomi")
    camera_id = models.IntegerField(verbose_name="Kamera ID", default=0)
    is_active = models.BooleanField(default=True, verbose_name="Faol")
    is_default = models.BooleanField(default=False, verbose_name="Asosiy kamera")
    last_used = models.DateTimeField(null=True, blank=True, verbose_name="Oxirgi ishlatilgan")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Kamera Qurilmasi"
        verbose_name_plural = "Kamera Qurilmalari"

    def __str__(self):
        status = "✅" if self.is_active else "❌"
        default = " ⭐" if self.is_default else ""
        return f"{self.name} (ID: {self.camera_id}) {status}{default}"


class FaceIDSession(models.Model):
    """Face ID monitoring sessiyasi"""
    camera = models.ForeignKey(
        CameraDevice, on_delete=models.SET_NULL,
        null=True, verbose_name="Kamera"
    )
    is_running = models.BooleanField(default=False, verbose_name="Ishlayapti")
    started_at = models.DateTimeField(null=True, blank=True, verbose_name="Boshlangan vaqt")
    stopped_at = models.DateTimeField(null=True, blank=True, verbose_name="To'xtatilgan vaqt")
    last_employee_seen = models.ForeignKey(
        'hr.Employee', on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name="Oxirgi ko'rilgan xodim"
    )
    total_check_ins = models.IntegerField(default=0, verbose_name="Jami kirishlar")
    total_check_outs = models.IntegerField(default=0, verbose_name="Jami chiqishlar")

    class Meta:
        verbose_name = "Face ID Sessiya"
        verbose_name_plural = "Face ID Sessiyalar"

    def __str__(self):
        status = "🟢 Ishlayapti" if self.is_running else "⚪ To'xtatilgan"
        return f"Face ID Session - {status}"
