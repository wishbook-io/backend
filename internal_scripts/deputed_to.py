from api.models import *
from django.contrib.auth.models import User, Group

company_users = CompanyUser.objects.filter(deputed_from__isnull=False).order_by('id')
for companyuser in company_users:
	print companyuser.id
	
	companyuser.deputed_to = companyuser.company
	companyuser.company = companyuser.deputed_from
	#companyuser.deputed_from = None
	companyuser.save()
	
