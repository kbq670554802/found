from django.db import models

from account.models import User


class Goods(models.Model):
    type = models.IntegerField(default=0, db_column='type')
    name = models.CharField(max_length=20, db_column='name')
    phone = models.CharField(max_length=20, db_column='phone')
    contact = models.CharField(max_length=100, db_column='contact')
    lost_date = models.DateField(auto_now_add=True, db_column='lost_date')
    lost_addr = models.CharField(max_length=100, db_column='lost_addr')
    summary = models.CharField(max_length=100, default='', db_column='summary')
    content = models.CharField(max_length=1000, db_column='content')
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, default=1, blank=True, db_column='user')
    create_time = models.DateTimeField(auto_now_add=True, db_column='create_time')
    modify_time = models.DateTimeField(auto_now=True, db_column='modify_time')


class PageInfo:
    page_index = 0,
    page_size = 0,
