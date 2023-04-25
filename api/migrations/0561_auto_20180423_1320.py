# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import audit_log.models.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('api', '0560_auto_20180421_1719'),
    ]

    operations = [
        migrations.AddField(
            model_name='imagetest',
            name='created_by',
            field=audit_log.models.fields.CreatingUserField(related_name='created_categories', editable=False, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='imagetest',
            name='created_with_session_key',
            field=audit_log.models.fields.CreatingSessionKeyField(max_length=40, null=True, editable=False),
        ),
    ]
