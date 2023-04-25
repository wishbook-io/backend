from django.forms import widgets
from rest_framework import serializers

##enter 1 pk Country value then apply migration
## python manage.py shell

from api.models import *
import IPython
#pip install ipython


userData = UserProfile.objects.all()
for udata in userData:udata.phone_number = udata.phone_number[-10:];udata.save();

userData = Company.objects.all().exclude(Q(phone_number__isnull=True) | Q(phone_number=''))
for udata in userData:udata.phone_number = udata.phone_number[-10:];udata.save();

userData = Branch.objects.all().exclude(Q(phone_number__isnull=True) | Q(phone_number=''))
for udata in userData:udata.phone_number = udata.phone_number[-10:];udata.save();

userData = Invitee.objects.all()
for udata in userData:udata.invitee_number = udata.invitee_number[-10:];udata.save();



userData = SalesOrder.objects.filter(processing_status="Pending").update(processing_status="Draft")
userData = SalesOrder.objects.filter(processing_status="ordered").update(processing_status="Placed")



userData = SalesOrder.objects.filter(processing_status="Draft").update(processing_status="Pending")
userData = SalesOrder.objects.filter(processing_status="Placed").update(processing_status="Accepted")

userData = SalesOrder.objects.filter(processing_status="dispatched").update(processing_status="Dispatched")
userData = SalesOrder.objects.filter(processing_status="delivered").update(processing_status="Delivered")
userData = SalesOrder.objects.filter(processing_status="cancelled").update(processing_status="Cancelled")

userData = SalesOrder.objects.filter(customer_status="pending").update(customer_status="Draft")
userData = SalesOrder.objects.filter(customer_status="finalized").update(customer_status="Placed")
userData = SalesOrder.objects.filter(customer_status="Payment_Confirmed").update(customer_status="Payment Confirmed")




userData = Push.objects.filter(status="schedule").update(status="Delivered")
userData = Push.objects.filter(status="delivered").update(status="Delivered")
userData = Push.objects.filter(status="pending").update(status="Delivered")
userData = Push.objects.filter(status="In_Progress").update(status="Delivered")


companyIds = CompanyType.objects.all().values_list("company", flat=True)
companyObj = Company.objects.all().exclude(id__in=companyIds)
for cdata in companyObj:CompanyType.objects.create(company=cdata)


cities = City.objects.all().values_list('id',flat=True)
categories = Category.objects.all().values_list('id',flat=True)
bs = BuyerSegmentation.objects.filter(segmentation_name__istartswith="All ")
for bso in bs: bso.city.add(*cities); bso.category.add(*categories); bso.save();

groups = GroupType.objects.all().values_list('id',flat=True)
bs = BuyerSegmentation.objects.filter(segmentation_name="All Buyers")
for bso in bs: bso.group_type.add(*groups); bso.save();


UserProfile.objects.update(phone_number_verified='yes')

#9 Agents to Broker (in group type
#change group_type name based on local
#change group_type name in buyer/supplier csv


#add warehouse and stock in admin's group panel

companyIds = Warehouse.objects.all().values_list("company", flat=True)
companyObj = Company.objects.all().exclude(id__in=companyIds)
for cdata in companyObj:Warehouse.objects.create(company=cdata, name=cdata.name+" warehouse")


catalogIds = Catalog.objects.all()
for cid in catalogIds: cid.categories = cid.category.first(); print cid.categories; cid.save();

productIds = Product.objects.all()
for cid in productIds: cid.catalogs = cid.catalog.first(); print cid.catalogs; cid.save();

companyIds = AppInstance.objects.all().values_list("company", flat=True)
companyObj = Company.objects.all().exclude(id__in=companyIds)
appObj = App.objects.get(pk=1)
for cdata in companyObj:AppInstance.objects.create(company=cdata, app=appObj)










##** temporary
from api.models import *
from django.db.models import Count
Buyer.objects.filter(Q(selling_company__in=[705, 151]) | Q(buying_company__in=[705, 151])).values('invitee__invitee_number').annotate(Count('invitee__invitee_number')).order_by().filter(invitee__invitee_number__count__gt=1)

Buyer.objects.filter(selling_company=705, status="Approved").update(selling_company=151)
Buyer.objects.filter(buying_company=705, status="Approved").update(buying_company=151)
Invitee.objects.filter(user=923).update(user=173)


Buyer.objects.filter(selling_company=151, status__in=["buyer_registrationpending", "supplier_registrationpending", "buyer_pending", "supplier_pending"], group_type=2).update(group_type=4)


users = User.objects.filter(email__icontains="@wishbooks.io").extra(where=["CHAR_LENGTH(email) = 23"])
for usr in users: usr.email=str(usr.userprofile.country.phone_code).replace("+", "")+usr.email; usr.save();


users = Company.objects.filter(email__icontains="@wishbooks.io").extra(where=["CHAR_LENGTH(email) = 23"])
for usr in users: usr.email="91"+usr.email; usr.save();


#delete all
com = Company.objects.filter(id__range=(537,540)).values_list('id',flat = True)
comuser = CompanyUser.objects.filter(company__in=com).values_list('user',flat = True)
User.objects.filter(id__in=comuser).delete()
Company.objects.filter(id__in=com).delete()

Invite.objects.all().delete()
Invitee.objects.all().delete()
Product.objects.all().delete()
RegistrationOTP.objects.all().delete()
# end delete all

#check buyer/supplier exist? in other company
sellingCom = Buyer.objects.filter(buying_company=229).values_list('selling_company', flat=True)
otherexistsellingCom = Buyer.objects.filter(selling_company__in=sellingCom).exclude(buying_company=229).values_list('selling_company', flat=True)
restSellingCom = list(set(sellingCom) - set(otherexistsellingCom))

buyingCom = Buyer.objects.filter(selling_company=229).values_list('buying_company', flat=True)
otherexistbuyingCom = Buyer.objects.filter(buying_company__in=buyingCom).exclude(selling_company=229).values_list('buying_company', flat=True)
restBuyingCom = list(set(buyingCom) - set(otherexistbuyingCom))

print restSellingCom
print restBuyingCom

restSellingComName =Company.objects.filter(id__in=restSellingCom).values_list('name', flat=True)
print restSellingComName

restBuyingComName =Company.objects.filter(id__in=restBuyingCom).values_list('name', flat=True)
print restBuyingComName
#end check buyer/supplier exist? in other company


#change city/ state
Company.objects.filter(id=1).update(state=State.objects.get(state_name=""), city=City.objects.get(city_name=""))


#end change city/ state

# =CONCATENATE("Company.objects.filter(id=",A2,").update(state=State.objects.get(state_name='",R2,"'), city=City.objects.get(city_name='",P2,"'))")

productList = Product.objects.filter(catalog__isnull=True, deleted = False).values_list('id')
print productList
selectionList = Selection.objects.filter(products__in=productList).values_list('user__username')
print selectionList

Product.objects.filter(catalog__isnull=True, deleted = False).update(deleted = True)

#UPDATE `api_product` SET `image`="product_image/blob_gEQ1mLZ"
#UPDATE `api_catalog` SET `thumbnail`="catalog_image/CV-MSHRE33988239320-Sarees-shreeharishop-Craftsvilla_1_zBIS0n8.jpg"
#UPDATE `api_brand` SET `image`="brand_image/images_6.jpg"


#for signup form
'''pip install django-allauth==0.26.1
pip install django-rest-auth==0.8.1


#ACCOUNT_SIGNUP_FORM_CLASS = 'api.forms.SignupForm'
REST_AUTH_SERIALIZERS = {
    'USER_DETAILS_SERIALIZER': 'api.v0.serializers.UserSerializer',
    'LOGIN_SERIALIZER': 'api.v0.serializers.LoginSerializer',
}

ACCOUNT_EMAIL_VERIFICATION = "none"

REST_AUTH_REGISTER_SERIALIZERS = {
    'REGISTER_SERIALIZER': 'api.v0.serializers.RegisterSerializer',
}



LAST_MODIFIED_FUNC = 'api.v0.views.last_modified'
'''

## on svn update n migrate
for so in SalesOrder.objects.all(): so.created_at = so.time; so.save()


#### new methods
#pip install ipython
from api.models import *
import IPython
from django.db.models import Sum, Min, Max

###for delete duplicate catalog
print " =====catalog===== "
max_catalog_push_user_ids = Push_User.objects.filter(catalog__isnull=False).values('user','selling_company', 'buying_company','catalog').annotate(id__max=Max('id')).values_list('id__max', flat=True)
print "max push_user unique"
print len(max_catalog_push_user_ids)

catalog_push_user_ids = []
catalog_push_user_product_ids = []

for row in Push_User.objects.filter(catalog__isnull=False).exclude(id__in=list(max_catalog_push_user_ids)).order_by('id'):
    pupids = Push_User_Product.objects.filter(push=row.push, user=row.user, selling_company=row.selling_company, buying_company=row.buying_company, catalog=row.catalog).values_list('id', flat=True)
    catalog_push_user_ids.append(row.id)
    catalog_push_user_product_ids.extend(pupids)
	
print "delete push_user id"
print len(catalog_push_user_ids)
print "delete push_user_product id"
print len(catalog_push_user_product_ids)

##use only want to delete
Push_User.objects.filter(id__in=catalog_push_user_ids).delete()
Push_User_Product.objects.filter(id__in=catalog_push_user_product_ids).delete()


###for delete duplicate selection
print " =====selection===== "
max_selection_push_user_ids = Push_User.objects.filter(selection__isnull=False).values('user','selling_company','buying_company','selection').annotate(id__max=Max('id')).values_list('id__max', flat=True)
print "max push_user unique"
print len(max_selection_push_user_ids)

selection_push_user_ids = []
selection_push_user_product_ids = []

for row in Push_User.objects.filter(selection__isnull=False).exclude(id__in=list(max_selection_push_user_ids)).order_by('id'):
    pupids = Push_User_Product.objects.filter(push=row.push, user=row.user, selling_company=row.selling_company, buying_company=row.buying_company, selection=row.selection).values_list('id', flat=True)
    selection_push_user_ids.append(row.id)
    selection_push_user_product_ids.extend(pupids)
	
print "delete push_user id"
print len(selection_push_user_ids)
print "delete push_user_product id"
print len(selection_push_user_product_ids)

##use only want to delete
Push_User.objects.filter(id__in=selection_push_user_ids).delete()
Push_User_Product.objects.filter(id__in=selection_push_user_product_ids).delete()


##remove unnecessary push
print " =====push===== "
pushids = Push_User.objects.all().values_list('push', flat=True).distinct()
pids=Push.objects.all().exclude(id__in=pushids).values_list('id', flat=True)
print "unnecessary push id"
print len(pids)
#Push.objects.filter(id__in=pids).delete()

## execfile('internal_scripts/remove_duplicate_share.py')

##remove unnecessary push_user
print "remove unnecessary push_user selection"
selection_push_user_ids = []
for row in Push_User.objects.filter(selection__isnull=False).order_by('id'):
    if not Push_User_Product.objects.filter(push=row.push, user=row.user, selling_company=row.selling_company, buying_company=row.buying_company, selection=row.selection).exists():
	selection_push_user_ids.append(row.id)
	
print "delete push_user id"
print len(selection_push_user_ids)
print selection_push_user_ids
#Push_User.objects.filter(id__in=selection_push_user_ids).delete()

print "remove unnecessary push_user catalog"
catalog_push_user_ids = []
for row in Push_User.objects.filter(catalog__isnull=False).order_by('id'):
    if not Push_User_Product.objects.filter(push=row.push, user=row.user, selling_company=row.selling_company, buying_company=row.buying_company, selection=row.selection).exists():
	catalog_push_user_ids.append(row.id)
	
print "delete push_user id"
print len(catalog_push_user_ids)
print catalog_push_user_ids
#Push_User.objects.filter(id__in=catalog_push_user_ids).delete()


#creating push temp table
for row in Push_User.objects.filter(catalog__isnull=False).order_by('id'):
	for pupObj in Push_User_Product.objects.filter(push=row.push, user=row.user, selling_company=row.selling_company, buying_company=row.buying_company, catalog=row.catalog):
		if CompanyProductFlat.objects.filter(product=pupObj.product, catalog=pupObj.catalog, buying_company=pupObj.buying_company).exists():
			cpfObj = CompanyProductFlat.objects.filter(product=pupObj.product, catalog=pupObj.catalog, buying_company=pupObj.buying_company).last()
			if cpfObj.final_price > pupObj.price or cpfObj.selling_company == pupObj.selling_company:
				print "update"
				buyer = Buyer.objects.filter(selling_company=pupObj.selling_company, buying_company=pupObj.buying_company).last()
				if buyer:
				    sellPrice = (pupObj.price+buyer.fix_amount) + ((pupObj.price*buyer.percentage_amount)/100)
				    cpfObj.final_price = pupObj.price
				    cpfObj.selling_price = sellPrice
				    cpfObj.selling_company = pupObj.selling_company
				    cpfObj.save()
		else:
			print "create"
			buyer = Buyer.objects.filter(selling_company=pupObj.selling_company, buying_company=pupObj.buying_company).last()
			if buyer:
			    sellPrice = (pupObj.price+buyer.fix_amount) + ((pupObj.price*buyer.percentage_amount)/100)
			    CompanyProductFlat.objects.create(product=pupObj.product, catalog=pupObj.catalog, buying_company=pupObj.buying_company, final_price=pupObj.price, selling_price=sellPrice, selling_company=pupObj.selling_company)

for row in Push_User.objects.filter(selection__isnull=False).order_by('id'):
	for pupObj in Push_User_Product.objects.filter(push=row.push, user=row.user, selling_company=row.selling_company, buying_company=row.buying_company, selection=row.selection):
		if CompanyProductFlat.objects.filter(product=pupObj.product, selection=pupObj.selection, buying_company=pupObj.buying_company).exists():
			cpfObj = CompanyProductFlat.objects.filter(product=pupObj.product, selection=pupObj.selection, buying_company=pupObj.buying_company).last()
			if cpfObj.final_price > pupObj.price or cpfObj.selling_company == pupObj.selling_company:
				print "update"
				buyer = Buyer.objects.filter(selling_company=pupObj.selling_company, buying_company=pupObj.buying_company).last()
				if buyer:
				    sellPrice = (pupObj.price+buyer.fix_amount) + ((pupObj.price*buyer.percentage_amount)/100)
				    cpfObj.final_price = pupObj.price
				    cpfObj.selling_price = sellPrice
				    cpfObj.selling_company = pupObj.selling_company
				    cpfObj.save()
		else:
			print "create"
			buyer = Buyer.objects.filter(selling_company=pupObj.selling_company, buying_company=pupObj.buying_company).last()
			if buyer:
			    sellPrice = (pupObj.price+buyer.fix_amount) + ((pupObj.price*buyer.percentage_amount)/100)
			    CompanyProductFlat.objects.create(product=pupObj.product, selection=pupObj.selection, buying_company=pupObj.buying_company, final_price=pupObj.price, selling_price=sellPrice, selling_company=pupObj.selling_company)

#execfile('internal_scripts/create_company_product_flat.py')



currentUserCompany=user.companyuser.company

companies = Company.objects.all()

for company in companies:		    
    pushUserProducts = Push_User_Product.objects.filter(buying_company=company, catalog__isnull=False).values('selling_company', 'product')
    
    Push_User_Product.objects.filter(buying_company=company, product__in=products).values('selling_company','buying_company','selection').annotate(id__max=Max('id')).values_list('id__max', flat=True)
    print pushUserProducts



pip install django-notifier

'notifier',

NOTIFIER_BACKENDS = (
    'api.v0.notifier_backend.EmailBackend',
    'api.v0.notifier_backend.SMS',
    'api.v0.notifier_backend.InApp',
)

'''
/notifier/groupprefs/

adm)	sales-order - email, sms, mobile, chat
adm)	purchase-order - email, sms, mobile, chat
adm)    buyer-request - sms, mobile, chat
adm)    supplier-request - sms, mobile, chat
adm, sp)    otp - sms
adm)    order-status - sms
'''

execfile('internal_scripts/remove_buyers.py')



#sellingPushUser = Push_User.objects.filter(push__in=sellingPushes, selling_company=selling_company).select_related('user').first()
catalogArr = Push_User.objects.filter(push__in=sellingPushes, selling_company=selling_company).exclude(catalog__isnull=True).values('catalog').annotate(Max('id')).values('id__max')#.distinct().values_list('id', flat=True)
print catalogArr
selectinArr = Push_User.objects.filter(push__in=sellingPushes, selling_company=selling_company).exclude(selection__isnull=True).values('selection').annotate(Max('id')).values('id__max')#.distinct().values_list('id', flat=True)
print selectinArr
sellPushUsers = Push_User.objects.filter(Q(id__in=catalogArr) | Q(id__in=selectinArr)).values_list('id', flat=True).distinct()

'''sellPushUsers = []
if sellingPushUser:
	sellingUser = sellingPushUser.user
	sellPushUsers = Push_User.objects.filter(push__in=sellingPushes, user=sellingUser, selling_company=selling_company).values_list('id', flat=True).distinct()'''


##check push is seller_company
	if puObj.selling_company == selling_company:
		pushUserProduct = Push_User_Product.objects.filter(push=puObj.push,user=puObj.user, catalog=catalog).select_related('product')
	

sellingUser to puObj.user


execfile('internal_scripts/buyer_supplier.py')
execfile('internal_scripts/remove_share.py')
execfile('internal_scripts/create_user_company.py')
execfile('internal_scripts/invitee_approve.py')
#on update eav
execfile('internal_scripts/eav_integration.py')
#then
#eav cron url
execfile('internal_scripts/applozic.py')
execfile('internal_scripts/chat_company.py')


'NON_FIELD_ERRORS_KEY': 'failed',



#pip install requests

pip install -U Celery
pip install django-celery
pip install sqlalchemy


'djcelery',

BROKER_URL = 'sqla+sqlite:///celerydb.sqlite'
CELERY_RESULT_BACKEND='djcelery.backends.cache:CacheBackend'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Kolkata'

# copy necessary files from project_settings folder

pip install Django==1.8.15
pip install djangorestframework==3.3.3

pip install --no-dependencies django-fcm


pip install drf-tracking
'rest_framework_tracking',


#add notifier grouppref for share

execfile('internal_scripts/invoice_push_date.py')




##for rest histry timezone error
http://stackoverflow.com/questions/21351251/database-returned-an-invalid-value-in-queryset-dates

What worked for me:

1. Populate the timezone definitions in the 'mysql' table

mysql_tzinfo_to_sql /usr/share/zoneinfo | mysql -u root -p mysql
2. Flush tables

mysql -u root -p -e "flush tables;" mysql 
3. Restart mysql

sudo service mysql restart



PRODUCT_SMALL_IMAGE = '150x210'
PRODUCT_MEDIUM_IMAGE = '700x980'

in REST_FRAMEWORK = {
'NON_FIELD_ERRORS_KEY': 'failed',
'DATETIME_FORMAT' : '%Y-%m-%d %I:%M:%S %p',

#to add buyers members in already created applogic group
execfile('internal_scripts/applozic_users.py')
execfile('internal_scripts/applozic_group_member.py')
execfile('internal_scripts/applozic_group.py')



pip install drf-nested-routers
execfile('internal_scripts/company_otp.py')

#urls.py
url(r'^api/v1/auth/', include('rest_auth.urls')),
url(r'^api/v1/auth/registration/', include('rest_auth.registration.urls')),
    

#sv sarees views
Push_User_Product.objects.filter(buying_company=252, is_viewed='yes').count()


SELECT * FROM `api_push_user_product` WHERE `buying_company_id`=175 or `selling_company_id`=175

received_view = Push_User_Product.objects.filter(buying_company=175, is_viewed='yes').count()

shared_view = Push_User_Product.objects.filter(selling_company=175, is_viewed='yes').count()


#use this before migrations
execfile('internal_scripts/buyer_segmentation.py')


execfile('internal_scripts/branch_info.py')
execfile('internal_scripts/register_invitee.py')

from api.models import *
CompanyProductFlat.objects.all().update(is_salable=False)


python manage.py migrate --fake api 0313_auto_20170325_1049


pip install django-daterange-filter


add notifier group pref 
administrator	order-status	mobile-notification
execfile('internal_scripts/attendance_visits.py')


pip install git+https://github.com/jleclanche/django-push-notifications.git@39989962fcfc852d0baca762ce95489512bd1ce5
pip install --upgrade pip
pip install apns2

PRIORITY_SMS_METHOD = 'smsSendSendSmart'
SHARE_SMS_LIMIT = 1

python manage.py fix_permissions


OTP_SMS_METHOD = 'msg91' #'smsSendICubes'

execfile('internal_scripts/attendance_visits.py')
execfile('internal_scripts/buyer_date.py')
execfile('internal_scripts/deputed_to.py')

execfile('internal_scripts/dailysharesms.py')

execfile('internal_scripts/user_password_change.py')
execfile('internal_scripts/buyer_created_type.py')


execfile('internal_scripts/buyer_send_sms.py')


execfile('internal_scripts/catalog_sort_order.py')


https://github.com/anx-ckreuzberger/django-rest-multiauthtoken


#Django Silver for Billing
#**need to upgrade this plugins for Silver**
pip install djangorestframework==3.3.2
pip install django-silver
pip install django-autocomplete-light==3.2.1
pip install sqlparse==0.2.3
pip install django-debug-toolbar==1.8

#**old plugins**
django-autocomplete-light (3.2.1)
pip install sqlparse==0.2.2
pip install django-debug-toolbar==1.4




INTERNAL_IPS = '127.0.0.1' #django debug toolbar
MAX_CATALOG_UPLOAD_LIMIT = 5


REST_AUTH_SERIALIZERS = {
    'USER_DETAILS_SERIALIZER': 'api.v1.serializers.UserSerializer',


execfile('internal_scripts/push_seller_price.py')

execfile('internal_scripts/product_view.py')

GLOBAL_SITE_URL = "http://app.wishbooks.io/"

pip install django-multiselectfield

execfile('internal_scripts/invitee_approve.py')

execfile('internal_scripts/enquiry_catalog.py')
execfile('internal_scripts/buyer_reject_update.py')

first cleanup rest_framework_tracking database table to speedup migrate

pip install drf-tracking==1.3.1

python manage.py migrate

==>site-packages/rest_framework_tracking/admin.py
#admin.site.register(APIRequestLog, APIRequestLogAdmin)
==>site-packages/rest_framework_tracking/mixins.py
def _clean_data(data):
    '''SENSITIVE_DATA = re.compile('api|token|key|secret|password|signature', re.I)
    CLEANSED_SUBSTITUTE = '********************'
    for key in data:
        if SENSITIVE_DATA.search(key):
            data[key] = CLEANSED_SUBSTITUTE'''
    return data



#for eav data changes
execfile('internal_scripts/eav.py')

#for push shared_catalog field update
execfile('internal_scripts/push_catalog_set.py')

execfile('internal_scripts/push_date.py')

from api.models import *
cids = CompanyType.objects.filter(manufacturer=False, wholesaler_distributor=False, retailer=True, online_retailer_reseller=False, broker=False).values_list('company', flat=True)
Company.objects.filter(id__in=cids).update(company_type='retailer')

#django after buyer invite logic change and added CompanyBrandFollow
#Committed revision 1401.

execfile('internal_scripts/buying_company_name.py')

execfile('internal_scripts/delete_wrong_number.py')
execfile('internal_scripts/disable_catalog.py')

execfile('internal_scripts/delete_invitee.py')

execfile('internal_scripts/enquiry_phone_change.py')

execfile('internal_scripts/delete_login_none_user.py')

execfile('internal_scripts/company_address_set.py')

#SELECT `id`, `sku`, `fabric`, `work` FROM `api_product` where (`fabric` like '_%' or `work` like '_%') order by `id` desc
#SELECT `api_product`.`id`, `sku`, `fabric`, `work`, `api_catalog`.`id` as catalog_id, `api_catalog`.`title` as catalog_title FROM `api_product` join `api_catalog` on `api_product`.`catalog_id`=`api_catalog`.`id` where (`fabric` like '_%' or `work` like '_%') order by `api_product`.`id` desc


GOOGLE_API_KEY = "AIzaSyCyG8H2bHMgsH-fTCEIHX1kWyq2vB51mQc"

execfile('internal_scripts/company_address_set.py')
execfile('internal_scripts/warehouse.py')


pip install django-multiselectfield == 0.1.8
'multiselectfield',
    
##'last_modified.middleware.LastModifiedMiddleware',
##LAST_MODIFIED_FUNC = 'api.v0.views.last_modified'


/api/v1/brandtotalcatalogcron/


copy /eav/ folder to /srt/django-eav/ 
djangorestframework (3.2.5) to 3.3.2

#add all fields in eav mapping

UPDATE `eav_attribute` SET `datatype`="multi" WHERE `name` in ("fabric","work")

execfile('internal_scripts/chat_company.py')
execfile('internal_scripts/company_address_set.py')

execfile('internal_scripts/eav_catalog.py')


execfile('internal_scripts/catalog_seller_public.py')


execfile('internal_scripts/meeting_address_latlong.py')



http://127.0.0.1:8000/api/v1/geocodelocationcron/

http://127.0.0.1:8000/api/v1/catalogeavcron/

'product_image': [
        ('full_size', 'url'),
        ('thumbnail_small', 'thumbnail__150x210'),
        ('thumbnail_medium', 'thumbnail__700x980')
    ],

    'catalog_image': [
        ('full_size', 'url'),
        ('thumbnail_small', 'thumbnail__150x210'),
        ('thumbnail_medium', 'thumbnail__357x500')
#       ('thumbnail_medium', 'thumbnail__535x750')
#       ('thumbnail_medium', 'thumbnail__700x980')
#       ('thumbnail_medium', 'thumbnail__400x562')

    ],


pip install django-q==0.8.1


pip install django-q==0.8.0

execfile('internal_scripts/user_profile_flag.py')



CACHE_EXPIRE_TIME = 3600
execfile('internal_scripts/supplier_person_name.py')

execfile('internal_scripts/buyer_reject_flag.py')


execfile('internal_scripts/user_login_issue.py')

execfile('internal_scripts/refer.py')


1.13.0
pip install django-datatables-view==1.14.0
0.2.1
pip install django-admin-rangefilter==0.3.1

execfile('internal_scripts/address_set_state_city.py')

execfile('internal_scripts/google_place.py')


execfile('internal_scripts/usercontact_onwishbook.py')


pip install WeasyPrint

execfile('internal_scripts/temp.py')


execfile('internal_scripts/refer_company.py') #send msg to refer_id company with lite link
execfile('internal_scripts/usercontact_onwishbook_csv.py') #export csv for onwishbook usercontacts
execfile('internal_scripts/usercontact_onwishbook.py') #send sms and register in wishbook using usercontact



url(r'^s/(?P<short_url>.+)$', RedirectToLongURL.as_view(), name='redirect_short_url'),
==>site-packages/rest_framework_tracking/models.py
class BaseAPIRequestLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)


http://127.0.0.1:8000/api/v1/cron/user-contact-registration/


#guest  company create
INSERT INTO `api_company`(`id`, `name`, `push_downstream`, `city_id`, `state_id`, `company_type`, `country_id`, `phone_number_verified`, `is_profile_set`, `paytm_country_id`) VALUES (1, "Guest", "no", 1, 1, "nonmanufacturer", 1, "yes", 0, 1);
INSERT INTO `api_companytype`(`company_id`) VALUES (1);


execfile('internal_scripts/guest_company_delete.py')

execfile('internal_scripts/keep_sakambari.py')


'category_image': [
        ('full_size', 'url'),
        ('thumbnail_small', 'thumbnail__'+SMALL_SQR_IMAGE)
    ],



update webapp - 

pip install django-audit-log
#in middlerware append at last
'audit_log.middleware.UserLoggingMiddleware',


add in Orders webapp
      {"text": "Sales Dashboard",       "sref": "app.orderdashboard"}

  {
    "text": "Marketing",
    "sref": "app.marketing",
    "icon": "fa fa-list",
    "label": "label label-success"
  },


1.4 to 1.9 #were using 1.4 to solve imange upload issue
pip install django-versatileimagefield==1.9

execfile('internal_scripts/delete_number_users.py')


update api_salesorder set order_type = 'Credit' where payment_details like "%credit%";


http://127.0.0.1:8000/api/v1/cron/inactive-user-notification-before-30-days/

execfile('internal_scripts/total_products_uploaded.py')


pip install django-impersonate==1.3.0
IMPERSONATE = {
    'REDIRECT_URL': '/'
}


https://github.com/silentsokolov/django-admin-rangefilter

pip install django-admin-rangefilter
'rangefilter',



execfile('internal_scripts/quickstart.py')

python internal_scripts/quickstart.py



symlink of google_sheet move to project

pip install --upgrade google-api-python-client
pip install --upgrade oauth2client

execfile('internal_scripts/urlindex_script.py')






