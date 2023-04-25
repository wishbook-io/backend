from django.conf import settings
import json
import requests

from api.models import *
from django.contrib.auth.models import User, Group

users = User.objects.all().order_by('id')

for user in users:
	#create user
	print "user.id"
	print user.id
	url = 'register/client'
	jsonarr = {"userId":user.username, "deviceType":"1", "applicationId":settings.APPLOZIC_APPID, "contactNumber":user.userprofile.phone_number}
	r = requests.post(settings.APPLOZIC_URL+url, data=json.dumps(jsonarr), headers=settings.APPLOZIC_HEADERS)
	print r
	print r.text
