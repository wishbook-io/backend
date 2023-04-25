from api.models import *

companies = Company.objects.filter(address__isnull=True).order_by('id')
for company in companies:
	print "company id =",company.id
	try:
		addressObj = Address.objects.create(name=company.name, city=company.city, state=company.state, street_address=company.street_address, pincode=company.pincode, country=company.country, user=company.chat_admin_user)
		company.address = addressObj
		company.save()
	except Exception as e:
		logger.info("in Exception error")
		logger.info(str(e))

branches = Branch.objects.filter(address__isnull=True).order_by('id')
for branch in branches:
	print "branch id =",branch.id
	branch.address = branch.company.address
	branch.save()
	
