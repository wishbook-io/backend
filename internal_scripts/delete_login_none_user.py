from api.models import *
#from api.v1.serializers import *
#from django.contrib.auth.models import User, Group
from datetime import datetime, date, time, timedelta

companies = Buyer.objects.filter(selling_company=27368).exclude(buying_company__isnull=True).values_list('buying_company', flat=True).distinct()
print companies
print len(companies)

users = CompanyUser.objects.filter(company__in=companies).exclude(user__isnull=True).values_list('user', flat=True).distinct()
print users
print len(users)

userObjs = User.objects.filter(id__in=users, last_login__isnull=True)
print userObjs.count()

#start_range = raw_input("Do you want to delete users (y/n) ")
print "for loop started -----"
for userObj in userObjs:
	print userObj.id
	print userObj.last_login

#userObjs.delete()
