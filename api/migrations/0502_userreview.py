# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import versatileimagefield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0501_auto_20171220_1612'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserReview',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('image', versatileimagefield.fields.VersatileImageField(upload_to=b'userreview_image/')),
                ('image_ppoi', versatileimagefield.fields.PPOIField(default='0.5x0.5', max_length=20, editable=False)),
                ('status', models.CharField(max_length=50, choices=[(b'Enable', b'Enable'), (b'Disable', b'Disable')])),
            ],
        ),
    ]
