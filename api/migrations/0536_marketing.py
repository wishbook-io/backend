# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('api', '0535_catalogenquiry'),
    ]

    operations = [
        migrations.CreateModel(
            name='Marketing',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('campaign_name', models.CharField(max_length=250)),
                ('campaign_text', models.CharField(max_length=250)),
                ('campaign_html', models.TextField(null=True, blank=True)),
                ('to', models.CharField(max_length=50, choices=[(b'All', b'All'), (b'Location', b'Location'), (b'Specific Numbers', b'Specific Numbers')])),
                ('specific_no_file', models.FileField(null=True, upload_to=b'marketing_files', blank=True)),
                ('company_number_type_all', models.BooleanField(default=False)),
                ('company_number_type_retailers', models.BooleanField(default=False)),
                ('company_number_type_wholesalers_agents', models.BooleanField(default=False)),
                ('company_number_type_manufactures', models.BooleanField(default=False)),
                ('company_number_type_guestusers', models.BooleanField(default=False)),
                ('company_number_type_inphonebook', models.BooleanField(default=False)),
                ('by_sms', models.BooleanField(default=False)),
                ('by_facebook_notifications', models.BooleanField(default=False)),
                ('by_in_app_notifications', models.BooleanField(default=False)),
                ('by_audio_call', models.BooleanField(default=False)),
                ('image', models.ImageField(default=None, null=True, upload_to=b'marketing_images', blank=True)),
                ('app_version', models.CharField(default=None, max_length=250, null=True, blank=True)),
                ('last_login_platform', models.CharField(default=None, max_length=20, null=True, blank=True, choices=[(b'Lite', b'Lite'), (b'Android', b'Android'), (b'iOS', b'iOS'), (b'Webapp', b'Webapp')])),
                ('deep_link', models.URLField(default=None, null=True, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('city', models.ManyToManyField(to='api.City', blank=True)),
                ('state', models.ManyToManyField(to='api.State', blank=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
