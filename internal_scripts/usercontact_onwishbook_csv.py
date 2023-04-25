from api.models import *
from django.contrib.auth.models import User, Group

from api.common_functions import getCompanyNumberFromNumber

import string
import random
import os
from decimal import Decimal
import csv

from api.v1.views import randomString

import dateutil
from django.conf import settings

import math

from django.db import connection


projectpath = os.getcwd()
print "projectpath =", projectpath


errorfilename = 'usercontact_found_onwishbook_csv_'+str(randomString())+'.csv'
errorfilepath = os.path.join(projectpath+"/internal_scripts/", errorfilename)

fieldnames = ['user', 'user_number', 'user_company', 'user_company_types', 'contact', 'contact_company', 'contact_company_type']

def ctypes(ct):
	arr = []
	if ct.manufacturer is True:
		arr.append('Manufacturer')
	if ct.wholesaler_distributor is True:
		arr.append('Wholesaler Distributor')
	if ct.retailer is True:
		arr.append('Retailer')
	if ct.online_retailer_reseller is True:
		arr.append('Online Retailer Reseller')
	if ct.broker is True:
		arr.append('Broker')
	return ", ".join(arr)

countryObj = Country.objects.get(pk=1)

print "csv file name ===========", errorfilename

with open(errorfilepath, "wb") as out_file:
	writer = csv.DictWriter(out_file, delimiter=',', fieldnames=fieldnames)
	writer.writeheader()
	
	# ~ limit = 50000
	# ~ completed_companies = []

	# ~ uctotal = UserContact.objects.count()
	# ~ print "uctotal =",uctotal

	# ~ no = math.ceil(float(uctotal)/float(limit))
	# ~ print "loop range =",no
	
	no = 1

	for i in range(int(no)):
		# ~ print "i =",i
		# ~ start = i*limit
		# ~ end = start+limit
		# ~ print "start =",start, "end=",end
		
		'''numbers = UserContact.objects.filter(id__gt=start, id__lte=end).values_list('number', flat=True)
		numbers = list(numbers)
		found_numbers = []
		usernumbers = UserProfile.objects.filter(phone_number__in=numbers).values_list('phone_number', flat=True)
		companyaliasnumbers = CompanyPhoneAlias.objects.filter(alias_number__in=numbers).values_list('company__phone_number', flat=True)
		companynumber = Company.objects.filter(phone_number__in=numbers).values_list('phone_number', flat=True)
		found_numbers.extend(list(usernumbers))
		found_numbers.extend(list(companyaliasnumbers))
		found_numbers.extend(list(companynumber))
		#print found_numbers
		
		ucObjs = UserContact.objects.filter(id__gt=start, id__lte=end, number__in=found_numbers).select_related('user__companyuser__company__company_group_flag','user__userprofile')
		'''
		
		#ucObjs = UserContact.objects.raw("select user_id, name, number from onwishbookcontacts order by user_id");
		cursor = connection.cursor()
		cursor.execute("select user_id, number, name from onwishbookcontacts order by user_id")
		cursor.fetchall()
		
		#for ucObj in ucObjs:
		for ucObj in cursor:
			try:
				#print "found=",ucObj
				print "number =",ucObj[1], "user_id =",ucObj[0]
				
				compnumber = getCompanyNumberFromNumber(countryObj, ucObj[1])
				country = compnumber[0]
				phone_number = compnumber[1]
				
				companyObj = Company.objects.filter(country=country, phone_number=phone_number).select_related('company_group_flag').last()
				if companyObj is None:
					continue
				
				# ~ user_company_types = ctypes(ucObj.user.companyuser.company.company_group_flag)
				# ~ contact_company_type = ctypes(companyObj.company_group_flag)
				
				# ~ jsonval = {"user":ucObj.user.username, "user_number":ucObj.user.userprofile.phone_number, "user_company":ucObj.user.companyuser.company.name.encode('utf-8'), "user_company_types":user_company_types, "contact":ucObj.number, "contact_company":companyObj.name.encode('utf-8'), "contact_company_type":contact_company_type}
				
				user = User.objects.get(pk=ucObj[0])
				user_company_types = ctypes(user.companyuser.company.company_group_flag)
				contact_company_type = ctypes(companyObj.company_group_flag)
				
				jsonval = {"user":user.username, "user_number":user.userprofile.phone_number, "user_company":user.companyuser.company.name.encode('utf-8'), "user_company_types":user_company_types, "contact":ucObj[1], "contact_company":companyObj.name.encode('utf-8'), "contact_company_type":contact_company_type}
				print jsonval
				writer.writerow(jsonval)
			except Exception as e:
				error = str(e)
				pass
			

print "csv file name ===========", errorfilename



