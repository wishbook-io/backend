# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('api', '0617_auto_20180730_1045'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('msg_way', models.CharField(default=b'Manual', max_length=100, choices=[(b'Manual', b'Manual'), (b'Automate', b'Automate')])),
                ('message', models.TextField(blank=True)),
                ('notifier_users', models.TextField(default=None, blank=True)),
                ('extra_ids', models.CharField(default=None, max_length=250, blank=True)),
                ('object_id', models.PositiveIntegerField(null=True, blank=True)),
                ('is_sent', models.BooleanField(default=False)),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='contenttypes.ContentType', null=True)),
                ('created_by', models.ForeignKey(related_name='trigger_notifications', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'notification',
                'verbose_name_plural': 'notifications',
            },
        ),
        migrations.CreateModel(
            name='NotificationEntity',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('entity_name', models.CharField(unique=True, max_length=100)),
            ],
            options={
                'verbose_name': 'notification entity',
                'verbose_name_plural': 'notification entities',
            },
        ),
        migrations.CreateModel(
            name='NotificationEntityTemplate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('label', models.CharField(max_length=250)),
                ('description', models.TextField(null=True, blank=True)),
                ('language', models.CharField(default=b'English', max_length=20, choices=[(b'Hindi', b'Hindi'), (b'English', b'English')])),
                ('is_sms', models.BooleanField(default=False)),
                ('sms_temp', models.TextField(default=None, blank=True)),
                ('is_notification', models.BooleanField(default=False)),
                ('notification_temp', models.TextField(default=None, blank=True)),
                ('is_email', models.BooleanField(default=False)),
                ('email_temp', models.TextField(default=None, blank=True)),
                ('is_inapp', models.BooleanField(default=False)),
                ('inapp_temp', models.TextField(default=None, blank=True)),
                ('receiver', models.CharField(default=None, max_length=250, blank=True)),
                ('entity', models.ForeignKey(verbose_name=b'notification entity', to='api.NotificationEntity')),
            ],
            options={
                'verbose_name': 'notification entity type',
                'verbose_name_plural': 'notification entity types',
            },
        ),
        migrations.AddField(
            model_name='notification',
            name='notice_template',
            field=models.ForeignKey(related_name='notifications', on_delete=django.db.models.deletion.SET_NULL, verbose_name=b'notice template', to='api.NotificationEntityTemplate', null=True),
        ),
        migrations.AlterUniqueTogether(
            name='notificationentitytemplate',
            unique_together=set([('entity', 'label')]),
        ),
    ]
