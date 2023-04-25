# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import versatileimagefield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0365_companyproductflat_is_viewed'),
    ]

    operations = [
        migrations.CreateModel(
            name='Promotion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('image', versatileimagefield.fields.VersatileImageField(upload_to=b'promotion_image/')),
                ('image_ppoi', versatileimagefield.fields.PPOIField(default='0.5x0.5', max_length=20, editable=False)),
                ('landing_page_type', models.CharField(max_length=50, choices=[(b'Tab', b'Tab'), (b'Html', b'Html')])),
                ('landing_page', models.CharField(max_length=100, null=True, blank=True)),
                ('start_date', models.DateField(null=True, blank=True)),
                ('end_date', models.DateField(null=True, blank=True)),
                ('status', models.CharField(max_length=50, choices=[(b'Enable', b'Enable'), (b'Disable', b'Disable')])),
                ('active', models.CharField(max_length=50, null=True, blank=True)),
            ],
        ),
    ]
