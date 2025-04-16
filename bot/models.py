import datetime

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class Update(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    telegram_id = models.BigIntegerField(default=0)
    message_id = models.BigIntegerField(default=0)
    from_id = models.BigIntegerField(default=0)
    chat_id = models.BigIntegerField(default=0)
    timestamp = models.BigIntegerField(default=0)
    from_username = models.CharField(max_length=256)
    text = models.TextField(null=True)
    raw = models.TextField(null=True)
    date_added = models.DateTimeField(null=True, auto_now=True)


class User(AbstractUser):
    id = models.AutoField(primary_key=True)
    telegram_account = models.CharField(max_length=255, null=True)
    telegram_chat_id = models.BigIntegerField(null=True)
    discord_account = models.CharField(max_length=255, null=True)
    ethereum_address = models.CharField(max_length=42, null=True)
    date_added = models.DateTimeField(null=True, auto_now=True)
    message_to_sign = models.TextField(null=True, blank=True)
    unique_token = models.TextField(null=True, blank=True)
    sign_successful = models.BooleanField(default=False)
