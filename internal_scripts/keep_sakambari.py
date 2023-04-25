from api.models import *
from api.v0.serializers import *
from django.contrib.auth.models import User, Group

from datetime import datetime, date, time, timedelta

sakambari_id = 148

companies_not_to_delete = Buyer.objects.filter(selling_company=sakambari_id, buying_company__isnull=False).values_list('buying_company', flat=True)
companies_not_to_delete = list(companies_not_to_delete)
companies_not_to_delete.append(sakambari_id)
companies_not_to_delete.append(1)

print "companies_not_to_delete =",companies_not_to_delete

user_not_to_delete = CompanyUser.objects.filter(company__in=companies_not_to_delete).values_list('user', flat=True).order_by('user')

print "user_not_to_delete =",list(user_not_to_delete)


##deleting
company_to_delete = Company.objects.all().exclude(id__in=companies_not_to_delete).values_list('id', flat=True).order_by('id')
print "company_to_delete =",list(company_to_delete)
#company_to_delete = Company.objects.all().exclude(id__in=companies_not_to_delete).delete()

final_user_to_delete = User.objects.all().exclude(id__in=user_not_to_delete).values_list('id', flat=True).order_by('id')
print "final_user_to_delete =",list(final_user_to_delete)
#final_user_to_delete = User.objects.all().exclude(id__in=user_not_to_delete).delete()


#Company.objects.filter(id=455).delete()

# ~ from django.db import connection
# ~ cursor = connection.cursor()
# ~ cursor.execute("DELETE FROM `api_company` WHERE id = %s", [1387])

company_to_deletes = Company.objects.all().exclude(id__in=companies_not_to_delete).order_by('id')
for company_to_delete in company_to_deletes:
	print "company_to_delete id =",company_to_delete.id
	company_to_delete.delete()

final_user_to_deletes = User.objects.all().exclude(id__in=user_not_to_delete).order_by('id')
for final_user_to_delete in final_user_to_deletes:
	print "final_user_to_delete id =",final_user_to_delete.id
	final_user_to_delete.delete()


