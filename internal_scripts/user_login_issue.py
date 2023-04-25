from api.models import *
from django.contrib.auth.models import User, Group

#~ companies = Company.objects.filter(is_profile_set=True, company_type_filled=False).order_by('id')
#~ print "total count=",companies.count()
#~ for company in companies:
	#~ print "company id=",company.id
	#~ ctObj, created = CompanyType.objects.get_or_create(company=company)
	#~ CompanyType.objects.filter(id=ctObj.id).update(retailer = True)

state = State.objects.filter(state_name="-").first()
city = City.objects.filter(city_name="-").first()

companies = Company.objects.filter(address__isnull=True).order_by('id')
print "total count=",companies.count()

for company in companies:
	print "company id=",company.id
	companyuserObj = CompanyUser.objects.filter(company=company).first()
	if companyuserObj:
		print "address create"
		user = companyuserObj.user
		addressObj = Address.objects.create(name=company.name, city=city, state=state, country=company.country, user=user)
		company.address = addressObj
		company.save()
	else:
		if not Catalog.objects.filter(company=company).exists():
			print "company delete"
			company.delete()

print "total count=",companies.count()

