from api.models import *

push_id = raw_input("push_id = ") 
#push_user_id = raw_input("push_user_id") 
buyer_id = raw_input("buyer_id or company_id = ") 

push_id = int(push_id)
#push_user_id = int(push_user_id)
buyer_id = int(buyer_id)

print "total shared to buying_company"
print Push_User.objects.filter(push=push_id, buying_company=buyer_id).count()

print "total shared by buying_company.... to selling_company"
print Push_User.objects.filter(push=push_id, selling_company=buyer_id).count()

print "flat total products buying_company"
print CompanyProductFlat.objects.filter(push_reference=push_id, buying_company=buyer_id).count()

print "flat total products selling_company"
print CompanyProductFlat.objects.filter(push_reference=push_id, selling_company=buyer_id).count()



todelete = raw_input("Are you want to delete (y/n) = ") 

if todelete == "y":
	print "deleting..."
	Push_User.objects.filter(push=push_id, buying_company=buyer_id).delete()
	Push_User.objects.filter(push=push_id, selling_company=buyer_id).delete()
	CompanyProductFlat.objects.filter(push_reference=push_id, buying_company=buyer_id).delete()
	CompanyProductFlat.objects.filter(push_reference=push_id, selling_company=buyer_id).delete()
	



