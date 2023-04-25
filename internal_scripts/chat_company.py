from api.models import *
from django.contrib.auth.models import User, Group


companyObjs = Company.objects.filter(chat_admin_user__isnull=True).order_by('id')

for companyObj in companyObjs:
	print "company id =", companyObj.id
	cuObj = CompanyUser.objects.filter(company=companyObj).order_by('id').first()
	if cuObj:
		companyObj.chat_admin_user = cuObj.user
		companyObj.save()
	else:
		print "user not found for company id =",companyObj.id
	
