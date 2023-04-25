# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import audit_log.models.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('api', '0561_auto_20180423_1320'),
    ]

    operations = [
        migrations.AddField(
            model_name='salesorder',
            name='created_by',
            field=audit_log.models.fields.CreatingUserField(related_name='created_salesorders', editable=False, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='salesorder',
            name='modified_by',
            field=audit_log.models.fields.LastUserField(related_name='modified_salesorders', editable=False, to=settings.AUTH_USER_MODEL, null=True),
        ),
    ]
