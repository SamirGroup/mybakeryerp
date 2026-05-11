from django.db import models
from django.contrib.auth.models import User


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
