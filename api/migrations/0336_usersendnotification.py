# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('api', '0335_buyer_user'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserSendNotification',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateField(auto_now_add=True)),
                ('send_sms', models.IntegerField(default=0)),
                ('send_chat', models.IntegerField(default=0)),
                ('send_gcm', models.IntegerField(default=0)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
