from api.models import *
from django.contrib.auth.models import User, Group

users = User.objects.filter(last_login__isnull=False).values_list('id', flat=True)
print "users=",list(users)

UserProfile.objects.filter(user__in=users).update(is_password_set=True)

users = User.objects.filter(is_active=False).values_list('id', flat=True)
print "users=",list(users)

UserProfile.objects.filter(user__in=users).update(user_approval_status="Pending")
