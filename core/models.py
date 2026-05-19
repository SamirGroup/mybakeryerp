from django.db import models
from django.contrib.auth.models import User


class TelegramSettings(models.Model):
    """Telegram bot sozlamalari — yagona qator (singleton)."""
    bot_token = models.CharField(max_length=200, blank=True, verbose_name="Bot Token")
    chat_id   = models.CharField(max_length=50, blank=True, verbose_name="Chat ID")
    is_active = models.BooleanField(default=True, verbose_name="Faol")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Telegram Sozlamalari"

    def __str__(self):
        return f"Telegram Bot {'✅' if self.is_active and self.bot_token else '❌'}"

    @classmethod
    def get(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
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
