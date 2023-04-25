# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0293_smserror'),
    ]

    operations = [
        migrations.AlterField(
            model_name='smserror',
            name='sms_text',
            field=models.TextField(),
        ),
    ]
