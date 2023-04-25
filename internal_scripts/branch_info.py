from api.models import *
from django.contrib.auth.models import User, Group

companyObjs = Company.objects.all().order_by('id')

for companyObj in companyObjs:
	print companyObj.id
	branchObj = Branch.objects.filter(company=companyObj).first()
	if branchObj:
		branchObj.city = companyObj.city
		branchObj.state = companyObj.state
		branchObj.street_address = companyObj.street_address
		branchObj.pincode = companyObj.pincode
		branchObj.country = companyObj.country
		branchObj.phone_number = companyObj.phone_number
		branchObj.save()




