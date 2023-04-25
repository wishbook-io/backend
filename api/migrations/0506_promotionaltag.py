# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import versatileimagefield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0505_auto_20171226_1853'),
    ]

    operations = [
        migrations.CreateModel(
            name='PromotionalTag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('image', versatileimagefield.fields.VersatileImageField(upload_to=b'userreview_image/')),
                ('image_ppoi', versatileimagefield.fields.PPOIField(default='0.5x0.5', max_length=20, editable=False)),
                ('status', models.CharField(default=b'Enable', max_length=20, choices=[(b'Enable', b'Enable'), (b'Disable', b'Disable')])),
                ('url', models.URLField(null=True, blank=True)),
            ],
        ),
    ]
