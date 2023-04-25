# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone
from django.conf import settings
import versatileimagefield.fields
import audit_log.models.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('api', '0562_auto_20180423_1453'),
    ]

    operations = [
        migrations.CreateModel(
            name='ImageTestAuditLogEntry',
            fields=[
                ('id', models.IntegerField(verbose_name='ID', db_index=True, auto_created=True, blank=True)),
                ('images', versatileimagefield.fields.VersatileImageField(upload_to=b'images_test/')),
                ('image_optional', versatileimagefield.fields.VersatileImageField(upload_to=b'images_test/', blank=True)),
                ('images_ppoi', versatileimagefield.fields.PPOIField(default='0.5x0.5', max_length=20, editable=False)),
                ('deleted', models.BooleanField(default=False)),
                ('created_with_session_key', audit_log.models.fields.CreatingSessionKeyField(max_length=40, null=True, editable=False)),
                ('action_id', models.AutoField(serialize=False, primary_key=True)),
                ('action_date', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('action_type', models.CharField(max_length=1, editable=False, choices=[('I', 'Created'), ('U', 'Changed'), ('D', 'Deleted')])),
                ('action_user', audit_log.models.fields.LastUserField(related_name='_imagetest_audit_log_entry', editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('created_by', audit_log.models.fields.CreatingUserField(related_name='_auditlog_created_categories', editable=False, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ('-action_date',),
                'default_permissions': (),
            },
        ),
    ]
