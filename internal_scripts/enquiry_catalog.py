from api.models import *
from api.v1.serializers import *
from django.contrib.auth.models import User, Group

buyers = Buyer.objects.filter(created_type="Enquiry", enquiry_catalog__isnull=True).order_by('id')

print buyers

for buyer in buyers:
	print "========================"
	print "buyer id ="
	print buyer.id
	try:
		details = buyer.details
		print details
		details = details.replace("u'", '"')
		details = details.replace("'", '"')
		details = json.loads(details)
		print details
		catalogid = details["catalog"]
		print "catalog id ="
		print catalogid
		buyer.enquiry_catalog = Catalog.objects.get(pk=catalogid)
		buyer.save()
	except Exception as e:
		logger.info("in Exception as e:")
		logger.info(str(e))
		pass
	





