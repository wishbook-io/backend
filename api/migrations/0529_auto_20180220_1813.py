# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
from django.utils.timezone import utc
import datetime


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('api', '0528_auto_20180220_1656'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserWishlist',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('catalog', models.ForeignKey(to='api.Catalog')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='predefinedfilter',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2018, 2, 20, 12, 43, 46, 60574, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
    ]
