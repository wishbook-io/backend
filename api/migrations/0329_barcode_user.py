# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('api', '0328_brand_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='barcode',
            name='user',
            field=models.ForeignKey(default=None, blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
    ]