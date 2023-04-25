# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('api', '0536_marketing'),
    ]

    operations = [
        migrations.AddField(
            model_name='companycatalogview',
            name='user',
            field=models.ForeignKey(default=None, blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AlterField(
            model_name='companycatalogview',
            name='company',
            field=models.ForeignKey(default=None, blank=True, to='api.Company', null=True),
        ),
        migrations.AlterUniqueTogether(
            name='companycatalogview',
            unique_together=set([('company', 'catalog', 'catalog_type', 'user')]),
        ),
    ]
