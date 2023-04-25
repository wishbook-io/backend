from api.models import *
from django.db import transaction
import glob
import re

print "before read file"
f=open('internal_scripts/buyers_sheet_import.csv', 'r')  

first_line = f.readline()[:-1].split(',')
print first_line

columns = {}
i = 0
for model in first_line:
    columns[model] = i
    i = i+1

print "after first_line"

err = ""

company_id = raw_input("company id: ") 

company = Company.objects.get(pk=company_id)##151

inviteeNotFound = 0
buyerNotFound = 0
buyerApproved = 0


try:
    with transaction.atomic():
	for line in f:
	    line = line[:-1].split(',')
	    #print line
	    fields = {}
	    for k,v in columns.iteritems():
		k = re.sub('[^a-zA-Z0-9-_ ]', '',k)
		fields[k] = re.sub('[^a-zA-Z0-9-_ ]', '',line[v])
	    
	    country_code = fields['country_code']
	    buyer_number = fields['buyer_number']
	    #buyer_name = fields['buyer_name']
	    group_type = fields['group_type']
	    
	    group_type = GroupType.objects.get(name=group_type)#(pk=4)
	    country = Country.objects.get(phone_code="+"+country_code)
	    
	    if UserProfile.objects.filter(country=country, phone_number=buyer_number).exists():
		userprofile = UserProfile.objects.filter(country=country, phone_number=buyer_number).first()
		if CompanyUser.objects.filter(user=userprofile.user).exists():
			buyer_number=userprofile.user.companyuser.company.phone_number
	    elif Company.objects.filter(country=country, phone_number=buyer_number).exists():
		print buyer_number
	    elif CompanyPhoneAlias.objects.filter(country=country, alias_number=buyer_number, status="Approved").exists():
		companyalias = CompanyPhoneAlias.objects.filter(country=country, alias_number=buyer_number, status="Approved").first()
		buyer_number = companyalias.company.phone_number
	    elif UnregisteredPhoneAlias.objects.filter(alias_country=country,alias_number=buyer_number).exists():
		unregister = UnregisteredPhoneAlias.objects.filter(alias_country=country,alias_number=buyer_number).first()
		buyer_number = unregister.master_number
		country = unregister.master_country
		    
	    
	    
	    
	    
	    inviteeObj = Invitee.objects.filter(invite__company=company, country=country, invitee_number=buyer_number).first()
	    
	    if inviteeObj:
		buyerObj = Buyer.objects.filter(selling_company=company, invitee=inviteeObj, group_type=group_type).first()
		if buyerObj:
		    buyerObj.delete()
		    inviteeObj.invite.delete()
		    inviteeObj.delete()
		    
		    #print "found buyer "+buyer_number
		    
		    if buyerObj.status == "approved":
			buyerApproved += 1
			print "approved "+buyer_number
		    
		else:
		    inviteeObj.invite.delete()
		    inviteeObj.delete()
		    buyerNotFound += 1
		    print "not found buyer "+buyer_number
	    else:
		inviteeNotFound += 1
		print "not found invitee "+buyer_number
	    
except Exception as e:
    print e
f.close()

print "inviteeNotFound = "+str(inviteeNotFound)
print "buyerNotFound = "+str(buyerNotFound)
print "buyerApproved = "+str(buyerApproved)

print ">>>>>>>>Successfully<<<<<<<<<<<"
