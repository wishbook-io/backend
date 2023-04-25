# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0380_auto_20170708_1712'),
    ]

    operations = [
        migrations.AlterField(
            model_name='promotion',
            name='landing_page_type',
            field=models.CharField(max_length=50, choices=[(b'Tab', b'Tab'), (b'Html', b'Html'), (b'Webview', b'Webview'), (b'support_chat', b'support_chat'), (b'faq', b'faq')]),
        ),
    ]
