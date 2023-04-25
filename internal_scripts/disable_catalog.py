from api.models import *
#from api.v1.serializers import *
#from django.contrib.auth.models import User, Group
from datetime import datetime, date, time, timedelta


lastdate =  datetime.strptime('2017-07-30', '%Y-%m-%d')
lastdate = datetime.combine(lastdate, datetime.max.time())
print "lastdate =", lastdate

catalogs = Catalog.objects.filter(created_at__lte=lastdate)
#catalogs = Catalog.objects.filter(created_at__lte=lastdate, id=444)
print "total catalogs =",catalogs.count()

for catalog in catalogs:
	print catalog.id
	print catalog.created_at
	
	psObj, created = CatalogSelectionStatus.objects.get_or_create(company=catalog.company, catalog=catalog)
	if psObj.status == "Enable":
		print "company = ", catalog.company.id, "Disable in if cond."
		psObj.status="Disable"
		psObj.save()
	
	catalog.supplier_disabled = True
	catalog.save()
	
	Push_User.objects.filter(catalog=catalog, push__date__lte=lastdate).update(supplier_disabled=True, buyer_disabled=True)
	
	buying_companies = Push_User.objects.filter(catalog=catalog, push__date__lte=lastdate).exclude(buying_company__isnull=True).values_list('buying_company', flat=True).distinct()
	print "buying_companies ",buying_companies
	companies = Company.objects.filter(id__in=buying_companies)
	for company in companies:
		print "push_user company = ", company.id, "Disable"
		psObj, created = CatalogSelectionStatus.objects.get_or_create(company=company, catalog=catalog)
		if psObj.status == "Enable":
			print "company = ", company.id, "Disable in if cond."
			psObj.status="Disable"
			psObj.save()



