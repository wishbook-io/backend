from api.models import *
from api.v1.serializers import *
from django.contrib.auth.models import User, Group

'''
companyObjs = Company.objects.all().order_by('id')
country = Country.objects.get(pk=1)

for company in companyObjs:
	#phonenumbers = []
	#print "next comp"
	phonenumbers = list(CompanyUser.objects.filter(company=company).values_list('user__userprofile__phone_number', flat=True).distinct())
	#phonenumbers.extend(companyuser)
	#print phonenumbers
	if company.phone_number not in phonenumbers:
		phonenumbers.extend([company.phone_number])
	alias = CompanyPhoneAlias.objects.filter(company=company, status="Approved").values_list('alias_number', flat=True).distinct()
	#if alias:
	phonenumbers.extend(alias)
	
	for phonenumber in phonenumbers:
		makeBuyerSupplierFromInvitee(phonenumber, country, company)
'''

country = Country.objects.get(pk=1)
phonenumbers = []

numbers = Buyer.objects.filter(selling_company__isnull=True, status="supplier_registrationpending").exclude(invitee__invitee_number__isnull=True).exclude(invitee__invitee_number__exact='').values_list('invitee__invitee_number', flat=True).distinct()
phonenumbers = list(numbers)

numbers = Buyer.objects.filter(buying_company__isnull=True, status="buyer_registrationpending").exclude(invitee__invitee_number__isnull=True).exclude(invitee__invitee_number__exact='').values_list('invitee__invitee_number', flat=True).distinct()
phonenumbers.extend(list(numbers))

print "buyer supplier pending phonenumbers length = "
print len(phonenumbers)

users = User.objects.filter(userprofile__phone_number__in=phonenumbers).order_by('id')
#########users = User.objects.filter(userprofile__phone_number__in=["2288996604"]).order_by('id')
print "total pending registered users length = "
print users.count()

print "buyer supplier pending phonenumbers = "
print phonenumbers
print "users = "
print users

for user in users:
	print user.id
	#print user.userprofile.phone_number
	if user.userprofile.phone_number != "" and user.userprofile.phone_number is not None and CompanyUser.objects.filter(user=user).exists()==True:
		print user.userprofile.phone_number
		makeBuyerSupplierFromInvitee(user.userprofile.phone_number, user.userprofile.country, user.companyuser.company)





