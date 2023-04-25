from api.models import *


buyerObjs = Buyer.objects.all().order_by('id')

for buyer in buyerObjs:
	print buyer.id
	if buyer.selling_company is not None and buyer.status not in ["supplier_registrationpending","supplier_pending","rejected"]:
		print "supplier_pending not"
		buyer.supplier_approval = True
	if buyer.buying_company  is not None and buyer.status not in ["buyer_registrationpending","buyer_pending","rejected"]:
		print "buyer_pending not"
		buyer.buyer_approval = True
	if buyer.supplier_approval == False and buyer.buyer_approval == False:
		print "false"
		buyer.buyer_approval = True
	buyer.save()

