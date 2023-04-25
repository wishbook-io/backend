# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('api', '0357_company_wishbook_salesman'),
    ]

    operations = [
        migrations.CreateModel(
            name='Jobs',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('job_type', models.CharField(max_length=20, choices=[(b'Buyer', b'Buyer'), (b'Supplier', b'Supplier')])),
                ('upload_file', models.FileField(null=True, upload_to=b'jobs_upload_file', blank=True)),
                ('error_file', models.FileField(null=True, upload_to=b'jobs_error_file', blank=True)),
                ('status', models.CharField(max_length=20, choices=[(b'Scheduled', b'Scheduled'), (b'In Progress', b'In Progress'), (b'Complete', b'Complete')])),
                ('completed_rows', models.IntegerField(default=0)),
                ('total_rows', models.IntegerField(default=0)),
                ('start_time', models.DateTimeField(null=True, blank=True)),
                ('end_time', models.DateTimeField(null=True, blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('company', models.ForeignKey(to='api.Company')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
