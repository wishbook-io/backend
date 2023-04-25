from api.models import *
from api.v0.serializers import *
from django.contrib.auth.models import User, Group

buyers = Buyer.objects.filter(invitee__isnull=False, buying_company_name__isnull=True).order_by('id')
#buyers = Buyer.objects.filter(invitee__isnull=False).order_by('id')
print "total buyers"
print buyers.count()
for buyer in buyers:
	print "buyer id = ", buyer.id
	try:
		invitee_name = buyer.invitee.invitee_name
		print invitee_name
		if buyer.buying_company:
			buyer.buying_company_name = buyer.buying_company.name
		else:
			buyer.buying_company_name = invitee_name
		buyer.buying_person_name = invitee_name
		buyer.save()
	except Exception as e:
		logger.info("in Exception error")
		logger.info(str(e))

	
orders = SalesOrder.objects.filter(buying_company_name__isnull=True).order_by('id')
#orders = SalesOrder.objects.filter().order_by('id')
print "total orders"
print orders.count()
for order in orders:
	print "order id = ", order.id
	order.buying_company_name = order.company.name
	print order.buying_company_name
	order.save()
	'''buyerObj = Buyer.objects.filter(selling_company=order.seller_company, buying_company=order.company).last()
	if buyerObj:
		order.buying_company_name = buyerObj.buying_company_name
		print order.buying_company_name
		order.save()'''
