from api.models import *

companies = Company.objects.filter(is_profile_set=False, company_type_filled=False, refer_id__isnull=True).exclude(id=1).order_by('id')
for company in companies:
	print "company id =",company.id, "phone number =",company.phone_number, "name =",company.name
	
	s = Buyer.objects.filter(selling_company=company).update(selling_company=None, status="supplier_registrationpending")
	if s>0:
		print "selling comp. to none = ",s
	b = Buyer.objects.filter(buying_company=company).update(buying_company=None, status="buyer_registrationpending")
	if b>0:
		print "buying comp. to none = ",b
	
	company.delete()
