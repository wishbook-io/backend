import datetime
import logging
from django.contrib.auth.models import User
from django.conf import settings
from celery.decorators import task
from django_q.tasks import async, result
from django_q.brokers import get_broker
from api.sugarcrm.client import *
logger = logging.getLogger(__name__)

#sugar crm access
def crm_access():
	client = Client("http://crm.wishbook.io", "webadmin", "022f868a091ca09260b98e37e9950346")
	return client


#for create company on crm
@task()
def update_company_to_crm(company_id, created):
	client = crm_access()
	from api.models import Company
	company  = Company.objects.get(pk=company_id)
	logger.info("company_id  %s ", company_id)
	try:
		name_value_list 					= {}
		name_value_list["name"] 			= company.name
		name_value_list["company_name_c"] 	= company.name
		if company.address:
			name_value_list["shipping_address_city"]   	= company.city.city_name
			name_value_list["shipping_address_state"]  	= company.state.state_name
			name_value_list["shipping_address_street"]	= company.street_address
		name_value_list["shipping_address_postalcode"] 	= company.pincode
		name_value_list["email1"] 					   	= company.email
		name_value_list["phone_office"] 			   	= company.phone_number
		name_value_list["wishbook_company_id_c"] 		= company.id
		if company.company_group_flag:
			arr = []
			ct  = company.company_group_flag
			if ct.manufacturer is True:
				arr.append('manufacturer')
			if ct.wholesaler_distributor is True:
				arr.append('wholesaler_distributor')
			if ct.retailer is True:
				arr.append('retailer')
			if ct.online_retailer_reseller is True:
				arr.append('online_retailer_reseller')
			if ct.broker is True:
				arr.append('broker')
			name_value_list["company_type_c"]	= "^"+"^,^".join(arr)+"^" #"^manufacturer^,^retailer^"
		if created:
			crm_company = client.set_entry("Accounts",name_value_list)
			company.sugar_crm_account_id = crm_company['id']
			if company.chat_admin_user and company.chat_admin_user.userprofile.sugar_crm_user_id:
				module_names  		=  ["Accounts"]
				module_ids    		=  [crm_company['id']]
				link_field_names	=  ["contacts"]
				related_ids  		=  [company.chat_admin_user.userprofile.sugar_crm_user_id]
				client.set_relationships(module_names,module_ids,link_field_names,related_ids)
			company.save()
		if not created:
				name_value_list["id"] = company.sugar_crm_account_id
				client.set_entry("Accounts",name_value_list)

	except Exception as e:
		logger.error("Exception" , exc_info=True)

@task()
#for user details updation to sugarcrm
def update_user_to_crm(user_id,created):
	import datetime
	logger.info("update_user_to_crm user_id  %s ", user_id)
	client = crm_access()
	try:
		user  									= User.objects.get(pk=user_id)
		name_value_list 						= {}
		name_value_list["first_name"] 			= user.userprofile.phone_number
		name_value_list["last_name"]  			= user.last_name
		name_value_list["last_login_platform"] 	= user.userprofile.last_login_platform
		if user.userprofile.first_login:
			name_value_list["first_login_date_c"] 	= "{}-{}-{}".format(user.userprofile.first_login.year, user.userprofile.first_login.month, user.userprofile.first_login.day)
		if user.date_joined:
			name_value_list["registration_date_c"] 	= "{}-{}-{}".format(user.date_joined.year, user.date_joined.month, user.date_joined.day)
		name_value_list["approval_status_c"] 	= user.userprofile.user_approval_status
		name_value_list["email1"] 				= user.email
		name_value_list["phone_mobile"] 		= user.userprofile.phone_number
		name_value_list["wishbook_user_id_c"] 	= user.id
		if created:
			crm_user = client.set_entry("Contacts",name_value_list)
			logger.info("update_user_to_crm crm contact id  %s ", crm_user['id'])
			user.userprofile.sugar_crm_user_id = crm_user['id']
			user.userprofile.save()
		if not created:
				name_value_list["id"] = user.userprofile.sugar_crm_user_id
				client.set_entry("Contacts",name_value_list)
	except Exception as e:
		logger.error("Exception" , exc_info=True)

@task()
def update_enquiry_to_crm(enquiry_id,created):
	client = crm_access()
	from api.models import CatalogEnquiry
	enquiry = CatalogEnquiry.objects.get(pk=enquiry_id)
	try:
		name_value_list	 = {}
		name_value_list["lead_type_c"] 				= enquiry.enquiry_type
		name_value_list["first_name"] 				= enquiry.catalog.title + " - " + enquiry.buying_company.name
		name_value_list["seller_company_account_c"] = enquiry.selling_company.name
		name_value_list["buyer_company_account_c"] 	= enquiry.buying_company.name
		name_value_list["catalog_name_c"] 			= enquiry.catalog.title
		name_value_list["enquiry_id_c"] 			= enquiry.id
		name_value_list["catalog_link_c"] 			= "https://app.wishbooks.io/#/app/products-detail/?type=publiccatalog&id="+ str(enquiry.catalog.id) + "&name=" + str(enquiry.catalog.title)
		name_value_list["enquiry_status_c"] 		= enquiry.status
		name_value_list["quantity_c"] 				= enquiry.item_quantity
		name_value_list["seller_company_number_c"] 	= enquiry.selling_company.phone_number
		name_value_list["buyer_company_number_c"] 	= enquiry.buying_company.phone_number
		name_value_list["description"] 				= enquiry.text
		name_value_list["enquiry_about_c"] 			= enquiry.text
		name_value_list["wishbook_enquiry_id_c"] 	= enquiry.id
		if created:
			crm_enquiry = client.set_entry("Leads",name_value_list)
			enquiry.sugar_crm_lead_id = crm_enquiry['id']
			enquiry.save()
			module_names  		=  ["Accounts"]
			if not enquiry.buying_company.sugar_crm_account_id:
				update_company_to_crm(enquiry.buying_company_id,True)
			module_ids    		=  [enquiry.buying_company.sugar_crm_account_id]
			link_field_names	=  ["leads"]
			related_ids  		=  [crm_enquiry['id']]
			client.set_relationships(module_names,module_ids,link_field_names,related_ids)
		if not created:
				name_value_list["id"] = enquiry.sugar_crm_lead_id
				client.set_entry("Leads",name_value_list)
	except Exception as e:
		logger.error("Exception" , exc_info=True)

def update_call_to_crm(user_id,call_type):
	import datetime
	logger.info("update_call_to_crm user_id  %s ", user_id)
	client = crm_access()
	user  									= User.objects.get(pk=user_id)
	call_value_list 						= {}
	if call_type == "invite_call":
		call_value_list["name"] 			= "Invite Call: " +  user.userprofile.phone_number
		call_value_list["type_c"] 			= "invited_user_call"
		da = user.date_joined + datetime.timedelta(days=1)
		call_value_list["date_start"] 	= "{}-{}-{}".format(da.year, da.month, da.day)
		call_value_list["description"] 	=  "Date joined  :" + "{}-{}-{}".format(user.date_joined.year,
																				  user.date_joined.month,
																				  user.date_joined.day
																				)
	if call_type == "welcome_call":
		call_value_list["name"] 			= "Welcome Call: " +  user.userprofile.phone_number
		call_value_list["type_c"] 			= "welcome_call"
		da = user.userprofile.first_login + datetime.timedelta(days=1)
		call_value_list["date_start"] 		= "{}-{}-{}".format(da.year, da.month, da.day)
		call_value_list["description"] 		=  "First login :" + "{}-{}-{}".format(user.userprofile.first_login.year,
																				  	user.userprofile.first_login.month,
																				  	user.userprofile.first_login.day
																				   )
	call_value_list["duration_minutes"] 	= "05"
	call_value_list["direction"] 			= "Outbound"

	if user.userprofile.sugar_crm_user_id:
		call_value_list["parent_id"] 		= user.userprofile.sugar_crm_user_id
	call_value_list["parent_type"] 			= "Contacts"
	call = client.set_entry("Calls",call_value_list)
	if user.userprofile.sugar_crm_user_id:
		module_names  		=  ["Contacts"]
		module_ids    		=  [user.userprofile.sugar_crm_user_id]
		link_field_names	=  ["calls"]
		related_ids  		=  [call['id']]
		client.set_relationships(module_names,module_ids,link_field_names,related_ids)


def user_to_crm(user_id,created):
	logger.info("user_to_crm user_id  %s ", user_id)

	if settings.TASK_QUEUE_METHOD == 'celery':
		task_id = update_user_to_crm.apply_async((user_id,), expires=datetime.now() + timedelta(days=2))

	elif settings.TASK_QUEUE_METHOD == 'djangoQ':
		task_id = async(
					'api.v1.sugar_crm.update_user_to_crm',
					user_id,
					created,
			)
# account update to crm
def company_to_crm_q(company_id,created):
    if settings.TASK_QUEUE_METHOD == 'celery':
    	task_id = update_company_to_crm.apply_async((company_id,), expires=datetime.now() + timedelta(days=2))
    elif settings.TASK_QUEUE_METHOD == 'djangoQ':
    	task_id = async(
    	'api.v1.sugar_crm.update_company_to_crm',
    	 company_id,
		 created,
    	)

#leads updates to crm
def enquiry_to_crm_q(enquiry_id,created):
    if settings.TASK_QUEUE_METHOD == 'celery':
    	task_id = update_enquiry_to_crm.apply_async((enquiry_id,), expires=datetime.now() + timedelta(days=2))
    elif settings.TASK_QUEUE_METHOD == 'djangoQ':
        print "inside company djangoq"
    	task_id = async(
    	'api.v1.sugar_crm.update_enquiry_to_crm',
    	 enquiry_id,
		 created,
    	)
