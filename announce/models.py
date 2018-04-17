from django.contrib.auth.models import User
from django.db import models


class Goods(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    lost_address = models.CharField(max_length=1000)
    contact_address = models.CharField(max_length=1000)
    phone = models.CharField(max_length=20)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    create_time = models.DateTimeField(auto_now_add=True)
    modify_time = models.DateTimeField(auto_now=True)
