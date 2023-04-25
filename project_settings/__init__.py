from __future__ import absolute_import
from .celery import app as celery_app


from django.contrib.auth.models import User

User._meta.get_field_by_name('email')[0]._unique = True



