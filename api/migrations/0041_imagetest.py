# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import versatileimagefield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0040_auto_20151219_0406'),
    ]

    operations = [
        migrations.CreateModel(
            name='ImageTest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('image', versatileimagefield.fields.VersatileImageField(upload_to=b'image_test/')),
                ('image_ppoi', versatileimagefield.fields.PPOIField(default='0.5x0.5', max_length=20, editable=False)),
            ],
        ),
    ]
