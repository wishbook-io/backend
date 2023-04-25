# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0164_auto_20160530_1214'),
    ]

    operations = [
        migrations.CreateModel(
            name='PromotionalNotification',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=200)),
                ('text', models.TextField()),
                ('category', models.ManyToManyField(to='api.Category')),
                ('city', models.ManyToManyField(to='api.City')),
                ('state', models.ManyToManyField(to='api.State')),
            ],
        ),
    ]
