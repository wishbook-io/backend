# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0188_auto_20160711_1239'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appinstance',
            name='app',
            field=models.ForeignKey(related_name='instance_app', to='api.App'),
        ),
        migrations.AlterField(
            model_name='appinstance',
            name='company',
            field=models.ForeignKey(related_name='instance_company', to='api.Company'),
        ),
        migrations.AlterField(
            model_name='appinstance',
            name='user',
            field=models.ForeignKey(related_name='instance_user', to=settings.AUTH_USER_MODEL),
        ),
    ]
