# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0112_auto_20160322_0622'),
    ]

    operations = [
        migrations.AddField(
            model_name='push',
            name='email',
            field=models.CharField(default=b'yes', max_length=5, choices=[(b'yes', b'Yes'), (b'no', b'No')]),
        ),
        migrations.AddField(
            model_name='push_user',
            name='email',
            field=models.CharField(default=b'yes', max_length=5, choices=[(b'yes', b'Yes'), (b'no', b'No')]),
        ),
        migrations.AddField(
            model_name='push_user',
            name='sms',
            field=models.CharField(default=b'yes', max_length=5, choices=[(b'yes', b'Yes'), (b'no', b'No')]),
        ),
        migrations.AddField(
            model_name='push_user',
            name='whatsapp',
            field=models.CharField(default=b'yes', max_length=5, choices=[(b'yes', b'Yes'), (b'no', b'No')]),
        ),
        migrations.AddField(
            model_name='push_user_product',
            name='email',
            field=models.CharField(default=b'yes', max_length=5, choices=[(b'yes', b'Yes'), (b'no', b'No')]),
        ),
        migrations.AddField(
            model_name='push_user_product',
            name='sms',
            field=models.CharField(default=b'yes', max_length=5, choices=[(b'yes', b'Yes'), (b'no', b'No')]),
        ),
        migrations.AddField(
            model_name='push_user_product',
            name='whatsapp',
            field=models.CharField(default=b'yes', max_length=5, choices=[(b'yes', b'Yes'), (b'no', b'No')]),
        ),
    ]
