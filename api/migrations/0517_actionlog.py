# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('api', '0516_auto_20180116_1757'),
    ]

    operations = [
        migrations.CreateModel(
            name='ActionLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('relationship_type', models.CharField(max_length=20, choices=[(b'Enquiry', b'Enquiry'), (b'Buyer', b'Buyer'), (b'Supplier', b'Supplier')])),
                ('action_type', models.CharField(max_length=20, choices=[(b'Call', b'Call'), (b'Chat', b'Chat')])),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('recipient_company', models.ForeignKey(to='api.Company')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
