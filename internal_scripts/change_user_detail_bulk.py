from api.models import *
from django.contrib.auth.models import User, Group

users = User.objects.all().order_by('id')

UserProfile.objects.all().update(phone_number = '0111122223')

for user in users:
	print user.id
	user.email = str(user.id)+'@wishbooks.io'
	user.save()

#execfile('internal_scripts/change_user_detail_bulk.py')
