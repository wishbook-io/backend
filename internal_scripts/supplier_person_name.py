from api.models import *
#from api.v0.serializers import *
from django.contrib.auth.models import User, Group

buyers = Buyer.objects.filter(invitee__invitation_type="Supplier", supplier_person_name__isnull=True).order_by('id')
print "total buyers"
print buyers.count()
for buyer in buyers:
	print "buyer id = ", buyer.id
	try:
		invitee_name = buyer.invitee.invitee_name
		print invitee_name
		buyer.supplier_person_name = invitee_name
		buyer.save()
	except Exception as e:
		logger.info("in Exception error")
		logger.info(str(e))
