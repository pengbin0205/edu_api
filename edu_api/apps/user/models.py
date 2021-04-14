from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.

class UserInfo(AbstractUser):
    """用户模型"""
    phone = models.CharField(max_length=11, unique=True, verbose_name="手机号")
    image = models.ImageField(upload_to='user', blank=True, null=True, verbose_name="用户头像")

    class Meta:
        db_table = "bz_user"
        verbose_name = "用户表"
        verbose_name_plural = verbose_name

