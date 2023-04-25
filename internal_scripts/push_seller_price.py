from api.models import *
from django.contrib.auth.models import User, Group
from django.db.models import Sum, Min, Max, Count
from datetime import datetime, date, time, timedelta


pup = Push_User_Product.objects.all().values('push', 'selling_company', 'product').annotate(Max('id')).values('id__max')
#pup = list(pup)
#print pup
print "push user product length = "
print len(pup)

pupObjs = Push_User_Product.objects.filter(id__in=pup).order_by('push', 'selling_company', 'product', 'price')
#print len(pupObjs)

for pupObj in pupObjs:
	print pupObj.push
	try:
		PushSellerPrice.objects.create(push=pupObj.push, selling_company=pupObj.selling_company, product=pupObj.product, price=pupObj.price)
	except Exception as e:
		print e
		pass
	
	
