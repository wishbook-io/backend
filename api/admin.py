from django.contrib import admin
from api.models import *
from api.v0.serializers import *
from api.v0.views import *

from api.v1.serializers import *
from api.v1.views import *
from api.common_functions import *

from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

from django.contrib import messages

import eav
from eav.forms import BaseDynamicEntityForm
from eav.admin import BaseEntityAdmin
eav.register(Product)
eav.register(Catalog)

#from exporthelpers import *

#from reversion.admin import VersionAdmin
#from simple_history.admin import SimpleHistoryAdmin

from import_export.admin import ImportExportModelAdmin, ExportMixin


from django.contrib.admin import SimpleListFilter

from easy_select2 import select2_modelform
from easy_select2 import select2_modelform_meta

admin.site.site_title = 'Wishbook - Catalog Sales B2B Application'
admin.site.site_header = 'Wishbook - Catalog Sales B2B Application'

from django.conf import settings


from rest_framework.authtoken.models import Token
from django.contrib.sessions.models import Session

from datetime import datetime, date, time, timedelta

from import_export import resources
from import_export import fields

#from api.tasks import *

#from daterange_filter.filter import DateRangeFilter
from rangefilter.filter import DateRangeFilter
from rest_framework_tracking.models import APIRequestLog

admin.site.register(ShipRocketApiLog)
admin.site.register(NotificationEntity)
admin.site.register(NotificationEntityTemplate)
admin.site.register(Notification)



class TokenAdmin(admin.ModelAdmin):
    list_display = ('key', 'user_id', 'user_detail')
    search_fields = ('key', 'user__username')
    raw_id_fields = ('user',)

    def user_detail(self, obj):
        return '<a href="%s" target="_blank">%s</a>' % ("/api/admin/auth/user/"+str(obj.user.id), obj.user.id)
    user_detail.allow_tags = True
    user_detail.short_description = 'User Details'
    user_detail.admin_order_field = 'user__id'

admin.site.unregister(Token)
admin.site.register(Token, TokenAdmin)

class SessionAdmin(admin.ModelAdmin):
    def _session_data(self, obj):
        return obj.get_decoded()
    list_display = ['session_key', '_session_data', 'user_detail', 'expire_date']
    search_fields = ('session_key',)

    def user_detail(self, obj):
        userid = obj.get_decoded()["_auth_user_id"]
        return '<a href="%s" target="_blank">%s</a>' % ("/api/admin/auth/user/"+str(userid), userid)
    user_detail.allow_tags = True
    user_detail.short_description = 'User Details'
    #user_detail.admin_order_field = 'user__id'

admin.site.register(Session, SessionAdmin)

'''
class APIRequestLogAdmin(admin.ModelAdmin):
    #date_hierarchy = 'requested_at'
    list_display = ('id', 'requested_at', 'response_ms', 'status_code',
                    'user', 'method',
                    'path', 'remote_addr', 'host',
                    'query_params')
    list_filter = ('method', 'status_code', 'requested_at', ('requested_at', DateRangeFilter))
    search_fields = ('path', 'user__username', 'method', 'remote_addr')
    raw_id_fields = ('user', )

    def get_queryset(self, request):
    	return super(APIRequestLogAdmin, self).get_queryset(request).select_related('user').order_by('-id')

admin.site.register(APIRequestLog, APIRequestLogAdmin)
'''

'''
class UserProfileInline(admin.TabularInline):
	model = UserProfile
	verbose_name_plural = 'User profile'

class UserNumberInline(admin.TabularInline):
	model = UserNumber
	extra = 1'''

# class UserNumberAdmin(admin.ModelAdmin):
# 	actions = [export_csv2]

admin.site.unregister(User)

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    max_num = 0
    can_delete = False
    raw_id_fields = ('user', 'warehouse')
    readonly_fields = ('modified',)

class UserFilter(SimpleListFilter):
    title = 'active users' # or use _('country') for translated title
    parameter_name = 'active_users'

    def lookups(self, request, model_admin):
        return (
            ('active_users', 'active users'),
        )

    def queryset(self, request, queryset):
		if self.value() == 'active_users':
			arr = []
			users = User.objects.filter().exclude(Q(date_joined__isnull=True) | Q(last_login__isnull=True)).order_by('-id')

			for userDetail in users:
				dateDiff = userDetail.last_login - userDetail.date_joined
				if dateDiff.days > 0:
					arr.append(userDetail.id)

			return queryset.filter(id__in=arr).order_by('-id')

class UserResource(resources.ModelResource):
	date_joined_date = fields.Field()
	last_login_date = fields.Field()
	first_login_date = fields.Field()
	company = fields.Field()
	state = fields.Field()
	city = fields.Field()
	manufacturer = fields.Field()
	wholesaler_distributor = fields.Field()
	retailer = fields.Field()
	online_retailer_reseller = fields.Field()
	broker = fields.Field()
	user_group = fields.Field()
	last_login_platform = fields.Field()
	uninstall_date = fields.Field()

	class Meta:
		model = User
		skip_unchanged = True
		report_skipped = False
		fields = ('id', 'username', 'first_name', 'last_name', 'email', 'userprofile__phone_number', 'company', 'user_group', 'state', 'city', 'manufacturer', 'wholesaler_distributor', 'retailer', 'online_retailer_reseller', 'broker', 'date_joined_date', 'last_login_date', 'first_login_date', 'is_staff', 'last_login_platform', 'uninstall_date')
		export_order = ('id', 'username', 'first_name', 'last_name',  'email', 'userprofile__phone_number', 'company', 'user_group', 'state', 'city', 'manufacturer', 'wholesaler_distributor', 'retailer', 'online_retailer_reseller', 'broker', 'date_joined_date', 'last_login_date', 'first_login_date', 'is_staff', 'last_login_platform', 'uninstall_date')
		widgets = {
		    #'date_joined': {'format': '%B %d, %Y, %I:%M%p'},
                }

	def get_queryset(self, request):
	    return super(UserResource, self).get_queryset(request).select_related('companyuser__company__address__state', 'companyuser__company__address__city').prefetch_related('address_set__state', 'address_set__city', 'groups')

	def dehydrate_company(self, user):
		try:
			global company
			company = None
			company = user.companyuser.company
			return company.name
		except:
			return ''

	def dehydrate_state(self, user):
		try:
			global company
			global address
			address = None
			#company = user.companyuser.company
			#return company.state.state_name
			try:
			    address = company.address
			except:
			    address = user.address_set.all()[0]
			return address.state.state_name
		except:
			return ''

	def dehydrate_city(self, user):
		try:
			global company
			global address
			#company = user.companyuser.company
			#return company.city.city_name
			return address.city.city_name
		except:
			return ''

	def dehydrate_manufacturer(self, user):
		try:
			global company
			global companyGroup
			companyGroup = None
			companyGroup = company.company_group_flag
			return companyGroup.manufacturer
		except:
			return ''

	def dehydrate_wholesaler_distributor(self, user):
		try:
			global companyGroup
			return companyGroup.wholesaler_distributor
		except:
			return ''

	def dehydrate_retailer(self, user):
		try:
			global companyGroup
			return companyGroup.retailer
		except:
			return ''

	def dehydrate_online_retailer_reseller(self, user):
		try:
			global companyGroup
			return companyGroup.online_retailer_reseller
		except:
			return ''

	def dehydrate_broker(self, user):
		try:
			global companyGroup
			return companyGroup.broker
		except:
			return ''


	def dehydrate_user_group(self, user):
		try:
			# ~ name = user.groups.all().values_list('name', flat=True).distinct()
			# ~ return ', '.join(name)
			names = []
			usergroups = user.groups.all()
			for usergroup in usergroups:
			    names.append(usergroup.name)
			return ', '.join(names)
		except:
			return ''

	def dehydrate_date_joined_date(self, user):
		try:
			return timezone.localtime(user.date_joined).strftime("%Y-%m-%d %H:%M:%S") #.strftime("%B %d, %Y, %I:%M%p")
		except:
			return ''

	def dehydrate_last_login_date(self, user):
		try:
			return timezone.localtime(user.last_login).strftime("%Y-%m-%d %H:%M:%S") #.strftime("%B %d, %Y, %I:%M%p")
		except:
			return ''

	def dehydrate_last_login_platform(self, user):
		try:
			return user.userprofile.last_login_platform
		except:
			return ''

	def dehydrate_first_login_date(self, user):
		try:
			return timezone.localtime(user.userprofile.first_login).strftime("%Y-%m-%d %H:%M:%S") #.strftime("%B %d, %Y, %I:%M%p")
		except:
			return ''

	def dehydrate_uninstall_date(self, user):
		try:
			return user.userprofile.uninstall_date
		except:
			return ''


class UserAdmin(ExportMixin, UserAdmin): #admin.ModelAdmin
    inlines = [UserProfileInline, ]
    '''fieldsets = (
        (None, {
            'fields': ('username', 'email', 'password')
        }),
    )'''
    add_fieldsets = (
      (None, {'fields':('username','email','password1','password2'),}),	#,'first_name','last_name'
    )
    list_display = ('id', 'username', 'email', 'phone', 'phone_verified', 'company_detail', 'user_group', 'date_joined', 'last_login', 'first_login', 'login_as', 'is_staff', 'is_active', 'last_login_platform', 'approval_status') #'whatsapp_verification',
    list_filter = ('date_joined', 'last_login', 'userprofile__first_login', 'is_staff', 'is_active', 'groups', 'userprofile__is_profile_set', 'userprofile__user_approval_status', 'userprofile__last_login_platform', UserFilter, ('date_joined', DateRangeFilter), ('last_login', DateRangeFilter), ('userprofile__first_login', DateRangeFilter))
    search_fields = ('id', 'username', 'email', 'userprofile__phone_number',  'companyuser__company__name' ) #'userprofile__whatsapp_verified',
    ordering = ('-id',)
    resource_class = UserResource
    #list_select_related = True
    #list_select_related = ('userprofile', 'companyuser__company')
    list_display_links = ('id',)
    #list_per_page = 10
    #date_hierarchy = 'last_login'
    # show_full_result_count = False

    def get_queryset(self, request):
    	return super(UserAdmin, self).get_queryset(request).select_related('userprofile', 'companyuser__company').prefetch_related('groups',)

    def login_as(self, obj):
        return '<a href="%s" target="_blank">%s</a>' % ("/api/admin/user/"+str(obj.id), obj.username)
    login_as.allow_tags = True
    login_as.short_description = 'Login as'

    def phone(self, obj):
    	try:
    	    phone = obj.userprofile.phone_number #Or change this to how you would access the userprofile object - This was assuming that the User, Profile relationship is OneToOne
    	    return phone
    	except:
    	    return ""
    phone.admin_order_field = 'userprofile__phone_number'

    def approval_status(self, obj):
    	try:
    	    approval_status = obj.userprofile.user_approval_status #Or change this to how you would access the userprofile object - This was assuming that the User, Profile relationship is OneToOne
    	    return approval_status
    	except:
    	    return ""
    approval_status.admin_order_field = 'userprofile__user_approval_status'

    def phone_verified(self, obj):
    	try:
    	    phone = obj.userprofile.phone_number_verified
    	    return phone
    	except:
    	    return ""
    phone_verified.admin_order_field = 'userprofile__phone_number_verified'

    # ~ def company(self, obj):
	# ~ try:
	    # ~ company = obj.companyuser.company.name
	    # ~ return company
	# ~ except:
	    # ~ return ""
    # ~ company.admin_order_field = 'companyuser__company__name'

    def company_detail(self, obj):
    	try:
    	    company = obj.companyuser.company

    	    return '<a href="%s" target="_blank">%s</a>' % ("/api/admin/api/company/"+str(company.id), company.name)
    	except:
    	    return ""
    company_detail.allow_tags = True
    company_detail.short_description = 'Company Details'
    company_detail.admin_order_field = 'companyuser__company__name'


    def whatsapp_verification(self, obj):
    	try:
    	    whatsapp_verified = obj.userprofile.whatsapp_verified
    	    return whatsapp_verified
    	except:
    	    return ""

    def first_login(self, obj):
    	try:
    	    first_login = obj.userprofile.first_login
    	    return first_login
    	except:
    	    return ""
    first_login.admin_order_field = 'userprofile__first_login'

    def last_login_platform(self, obj):
    	try:
    	    last_login_platform = obj.userprofile.last_login_platform
    	    return last_login_platform
    	except:
    	    return ""

    def user_group(self, obj):
    	try:
            # ~ name = obj.groups.all().values_list('name', flat=True).distinct()
            # ~ return ', '.join(name)
            names = []
            usergroups = obj.groups.all()
            for usergroup in usergroups:
                names.append(usergroup.name)
            return ', '.join(names)
    	except:
    	    return ""



def user_unicode(self):
    #return  u'%s, %s' % (self.last_name, self.first_name)
    return  '%s : %s : %s %s' % (self.id, self.username, self.first_name, self.last_name)

User.__unicode__ = user_unicode

admin.site.register(User, UserAdmin)

'''
class CatalogAdmin(VersionAdmin):

    pass

class Push_UserAdmin(VersionAdmin):

    pass

class SalesOrderAdmin(VersionAdmin):

    pass

class SalesOrderItemAdmin(VersionAdmin):

    pass
'''
class SoftDeleteAdmin(admin.ModelAdmin):
    list_display = ('id', 'images', 'deleted',)
    list_filter = ('deleted',)
    def get_queryset(self, request):
	""" Returns a QuerySet of all model instances that can be edited by the
	admin site. This is used by changelist_view. """
	# Default: qs = self.model._default_manager.get_query_set()
	qs = self.model._default_manager.all_with_deleted()
	# TODO: this should be handled by some parameter to the ChangeList.
	ordering = self.ordering or () # otherwise we might try to *None, which is bad ;)
	if ordering:
	    qs = qs.order_by(*ordering)
	return qs


class UserProfileAdmin(admin.ModelAdmin):
	list_display = ('id', 'user', 'alternate_email', 'phone_number', 'user_image', )
	#list_filter = ('id', 'name', 'company', )
	search_fields = ('id', 'user__username', 'alternate_email', 'phone_number', )
	raw_id_fields = ('user', 'warehouse')

	def get_queryset(self, request):
	    return super(UserProfileAdmin, self).get_queryset(request).select_related('user')

admin.site.register(UserProfile, UserProfileAdmin)

###admin.site.register(Choice)

def make_downstream_yes(modeladmin, request, queryset):
    queryset.update(push_downstream='yes')
make_downstream_yes.short_description = "Mark selected companies as downstream=Yes"

def make_downstream_no(modeladmin, request, queryset):
    queryset.update(push_downstream='no')
make_downstream_no.short_description = "Mark selected companies as downstream=No"

class CompanyResource(resources.ModelResource):
	#invited_by_company = fields.Field()
	#invited_by_user = fields.Field()
	#invited_city = fields.Field()
	#invited_state = fields.Field()
	#users = fields.Field()
	#registered_date = fields.Field()
	last_login = fields.Field()
	company_types = fields.Field()
	total_catalog = fields.Field()
	last_catalog_upload = fields.Field()
	#last_catalog_shared = fields.Field()
	#total_buyer_approved = fields.Field()
	total_sales = fields.Field()
	total_purchase = fields.Field()

	address_city = fields.Field()
	address_state = fields.Field()

	class Meta:
		model = Company
		skip_unchanged = True
		report_skipped = False
		fields = ('id', 'name', 'phone_number', 'phone_number_verified', 'last_login', 'total_catalog', 'last_catalog_upload', 'total_sales', 'total_purchase', 'wishbook_salesman', 'company_types', 'address_city', 'address_state')
		export_order = ('id', 'name', 'phone_number', 'phone_number_verified', 'last_login', 'total_catalog', 'last_catalog_upload', 'total_sales', 'total_purchase', 'wishbook_salesman', 'company_types', 'address_city', 'address_state')#'invited_city', 'invited_state', 'status',

	def get_queryset(self, request):
	    #return super(CompanyResource, self).get_queryset(request).select_related('city', 'state', 'country')
	    return super(CompanyResource, self).get_queryset(request).select_related('address__state', 'address__city', 'company_group_flag').prefetch_related('company_users__user')

	def dehydrate_address_city(self, obj):
	    try:
		global address
		address = None
		address = obj.address
		return address.city.city_name
	    except:
		return ""

	def dehydrate_address_state(self, obj):
	    try:
		global address
		return address.state.state_name
	    except:
		return ""

	'''def dehydrate_invited_by_company(self, obj):
		try:
			global user
			global invitee

			user = CompanyUser.objects.filter(company=obj).first().user
			#name = Invitee.objects.filter(invitee_number = obj.phone_number, country=obj.country, invite__time__lte=user.date_joined).values_list('invite__company__name', flat=True).first()
			invitee = Invitee.objects.filter(invitee_number = obj.phone_number, country=obj.country, invite__time__lte=user.date_joined+timedelta(hours=12)).select_related('invite__company__city', 'invite__user').first()#values_list('invite__company__name', flat=True).

			return invitee.invite.company.name
			#return ', '.join(name)
		except:
			return ''
	'''
	'''def dehydrate_invited_by_user(self, obj):
		try:
			global invitee
			return invitee.invite.user.username
		except:
			return ''
	'''
	'''
	def dehydrate_invited_city(self, obj):
		try:
			global invitee
			return invitee.company.city.city_name
		except:
			return ''

	def dehydrate_invited_state(self, obj):
		try:
			global invitee
			return invitee.company.state.state_name
		except:
			return ''
	'''

	'''def dehydrate_users(self, obj):
		try:
			users = CompanyUser.objects.filter(company=obj).values_list('user__username', flat=True).distinct()

			return ', '.join(users)
		except:
			return ''
	'''
	'''def dehydrate_registered_date(self, obj):
		try:
			global user
			#user = CompanyUser.objects.filter(company=obj).first().user

			return timezone.localtime(user.date_joined).strftime("%B %d, %Y, %I:%M%p")
		except:
			return ''
	'''
	def dehydrate_last_login(self, obj):
		try:
			global user
			#user = CompanyUser.objects.filter(company=obj).first().user
			com_users = obj.company_users.all()
			user = com_users[0].user
			return timezone.localtime(user.last_login).strftime("%B %d, %Y, %I:%M%p")
		except:
			return ''

	def dehydrate_company_types(self, obj):
		try:
			ct = obj.company_group_flag
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
		except:
			return ""

	def dehydrate_total_catalog(self, obj):
		try:
			totalc = Catalog.objects.filter(company=obj).count()
			return totalc

			return ""
		except:
			return ""

	def dehydrate_last_catalog_upload(self, obj):
		try:
			cObj = Catalog.objects.filter(company=obj).order_by('-id').first()
			if cObj:
			    return cObj.created_at

			return ""
		except:
			return ""

	# ~ def dehydrate_last_catalog_shared(self, obj):
		# ~ try:
			# ~ puObj = Push.objects.filter(company=obj).order_by('-id').first()
			# ~ if puObj:
			    # ~ return puObj.date

			# ~ return ""
		# ~ except:
			# ~ return ""

	# ~ def dehydrate_total_buyer_approved(self, obj):
		# ~ try:
			# ~ return Buyer.objects.filter(selling_company=obj, status="approved").count()
		# ~ except:
			# ~ return ""

	def dehydrate_total_sales(self, obj):
		try:
			return SalesOrder.objects.filter(seller_company=obj).count()
		except:
			return ""

	def dehydrate_total_purchase(self, obj):
		try:
			return SalesOrder.objects.filter(company=obj).count()
		except:
			return ""

class CompanyLastLoginFilter(SimpleListFilter):
    title = 'last login' # or use _('country') for translated title
    parameter_name = 'last_login'

    def lookups(self, request, model_admin):
        return (
            ('last_login', 'last login'),
        )

    def queryset(self, request, queryset):
		if self.value() == 'last_login':
			arr = []
			companies = CompanyUser.objects.filter().exclude(Q(user__date_joined__isnull=True) | Q(user__last_login__isnull=True)).values_list('company', flat=True)

			return queryset.filter(id__in=companies).order_by('-id')

CompanyForm = select2_modelform(Company, attrs={'width': '250px'})
class CompanyAdmin(ExportMixin, admin.ModelAdmin):
	list_display = ('id', 'name', 'push_downstream', 'phone_number', 'email', 'users', 'registered_date', 'last_login', 'status', 'company_type', 'address_city', 'address_state', 'company_types', 'wishbook_salesman')#, 'last_catalog_upload', 'total_buyer_approved', 'invited_by_company', 'invited_by_user', 'invited_city'
	list_filter = ('push_downstream', 'status', 'company_type', 'trusted_seller', 'is_profile_set', 'address__state', CompanyLastLoginFilter)
	search_fields = ('id', 'name', 'phone_number', 'email', 'company_type', 'address__city__city_name', 'address__state__state_name', 'wishbook_salesman')
	filter_horizontal = ('category', )
	actions = [make_downstream_yes, make_downstream_no, 'generate_invoice', 'generate_credit']
	raw_id_fields = ('country', 'state', 'city', 'chat_admin_user', 'paytm_country', 'address', 'refered_by')
	resource_class = CompanyResource
	form = CompanyForm
	readonly_fields = ('created', 'modified',)

	#only view permission
	# ~ def get_readonly_fields(self, request, obj=None):
	    # ~ readonly_fields = []
	    # ~ for field in self.model._meta.fields:
		# ~ readonly_fields.append(field.name)

	    # ~ return readonly_fields

	# ~ save_as = True
	# ~ save_on_top = True
	# ~ change_list_template = 'change_list_graph.html'

	def get_queryset(self, request):
	    return super(CompanyAdmin, self).get_queryset(request).select_related('address__state', 'address__city', 'country', 'company_group_flag').prefetch_related('company_users__user')

	def generate_credit(self, request, queryset):
	    if request.POST.get('post'):
		print "Post generate_credit"
		print queryset

		#ids = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
		ids = queryset.values_list('id', flat=True).distinct()
		ids = list(ids)
		amount = request.POST.get('amount')
		expire_date = request.POST.get('expire_date')

		print ids
		print amount
		print expire_date

		if settings.TASK_QUEUE_METHOD == 'celery':
		    gi = generateCredit.apply_async((ids, amount, expire_date), expires=datetime.now() + timedelta(days=2))
		    print gi
		elif settings.TASK_QUEUE_METHOD == 'djangoQ':
		    task_id = async(
			    'api.tasks.generateCredit',
			    ids, amount, expire_date
		    )

		'''for company in queryset:
		    #company = Company.objects.get(pk=cid)
		    Credit.objects.create(company=company, amount=amount, balance_amount=amount, expire_date=expire_date)
		'''

		self.message_user(request, "Credit has been created!")
	    else:
		print "Form"

		context = {
		    'title': "Create Credit",
		    'queryset': queryset,
		    'action_checkbox_name': helpers.ACTION_CHECKBOX_NAME,
		}
		return TemplateResponse(request, 'admin/api/company/generate_credit.html', context, current_app=self.admin_site.name)

	generate_credit.short_description = u'Generate Credit'

	def generate_invoice(self, request, queryset):
	    '''todayDate = date.today()

	    currentMonthStartDate = todayDate.replace(day=1)

	    lastMonthEndDate = currentMonthStartDate - timedelta(days=1)
	    lastMonthStartDate = lastMonthEndDate.replace(day=1)'''

	    #ids = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
	    ids = queryset.values_list('id', flat=True).distinct()
	    ids = list(ids)
	    #print ids

	    if settings.TASK_QUEUE_METHOD == 'celery':
		gi = generateInvoice.apply_async((ids, True), expires=datetime.now() + timedelta(days=2))
		print gi
	    elif settings.TASK_QUEUE_METHOD == 'djangoQ':
		task_id = async(
			'api.tasks.generateInvoice',
			ids, True
		)

	    '''for company in queryset:
		invoice = Invoice.objects.filter(company=company, start_date=lastMonthStartDate, end_date=lastMonthEndDate).first()
		if invoice:
		    invoice_ser = InvoiceSerializer(invoice, data={}, partial=True)
		    if invoice_ser.is_valid():
			invoice_ser.save()
		    else:
			print invoice_ser.errors
		else:
		    invoice_ser = InvoiceSerializer(data={'company':company.id, 'start_date':lastMonthStartDate, 'end_date':lastMonthEndDate})
		    if invoice_ser.is_valid():
			invoice_ser.save()
		    else:
			print invoice_ser.errors'''

	    messages.success(request, 'Invoice generated successfully')
	    return
	generate_invoice.short_description = u'Generate/Re-generate Invoice'

	# ~ def invited_by_company(self, obj):
	    # ~ try:
		# ~ global user
		# ~ global invitee
		# ~ user = obj.company_users.all()[0].user

		# ~ invitee = Invitee.objects.filter(invitee_number = obj.phone_number, country=obj.country, invite__time__lte=user.date_joined+timedelta(hours=12)).select_related('invite__company__city', 'invite__user').first()

		# ~ return invitee.invite.company.name

	    # ~ except:
		# ~ return ""

	# ~ def invited_by_user(self, obj):
	    # ~ try:
		# ~ global invitee
		# ~ return invitee.invite.user.username

	    # ~ except:
		# ~ return ""

	# ~ def invited_city(self, obj):
	    # ~ try:
		# ~ global invitee
		# ~ return invitee.company.city.city_name

	    # ~ except:
		# ~ return ""

	#~ def users(self, obj):
	    #~ try:
		#~ global com_users
		#~ com_users = obj.company_users.all()

		#~ names = []
		#~ for com_user in com_users:
		    #~ names.append(com_user.user.username)
		#~ return ', '.join(names)

	    #~ except:
		#~ return ""
	def users(self, obj):
	    try:
			global com_users
			com_users = obj.company_users.all()

			names = []
			for com_user in com_users:
				names.append('<a href="%s" target="_blank">%s</a>' % ("/api/admin/auth/user/"+str(com_user.user.id), com_user.user.username))
			return ', '.join(names)
	    except:
			return ""
	users.allow_tags = True
	users.short_description = 'Users'

	def registered_date(self, obj):
	    try:
		global com_users
		global user
		user = com_users[0].user

		#user = CompanyUser.objects.filter(company=obj).first().user
		return user.date_joined

	    except:
		return ""

	def last_login(self, obj):
	    try:
		global user
		#user = CompanyUser.objects.filter(company=obj).first().user
		return user.last_login

	    except:
		return ""

	def company_types(self, obj):
	    try:

		#ct = CompanyType.objects.get(company=obj.id)
		ct = obj.company_group_flag
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
	    except:
		return ""

	def address_city(self, obj):
	    try:
		global address
		address = None
		address = obj.address
		return address.city.city_name
	    except:
		return ""

	def address_state(self, obj):
	    try:
		global address
		return address.state.state_name
	    except:
		return ""

	# ~ def last_catalog_upload(self, obj):
	    # ~ try:

		# ~ cObj = Catalog.objects.filter(company=obj).order_by('-id').first()
		# ~ if cObj:
		    # ~ return cObj.created_at

		# ~ return ""
	    # ~ except:
		# ~ return ""

	# ~ def total_buyer_approved(self, obj):
	    # ~ try:
		# ~ return Buyer.objects.filter(selling_company=obj, status="approved").count()
	    # ~ except:
		# ~ return ""

admin.site.register(Company, CompanyAdmin)


from django.contrib.admin import helpers
from django.template.response import TemplateResponse

#from rest_framework.response import Response
from django.http import HttpResponseRedirect

class UserCompanyDetailResource(resources.ModelResource):
	person_name = fields.Field()
	phone = fields.Field()
	is_profile_set = fields.Field()
	company = fields.Field()
	invited_by_company = fields.Field()
	invite_type = fields.Field()
	state = fields.Field()
	city = fields.Field()
	user_type = fields.Field()
	buyer_invited = fields.Field()
	buyer_registered = fields.Field()
	buyer_approved = fields.Field()
	supplier_invited = fields.Field()
	supplier_registered = fields.Field()
	supplier_approved = fields.Field()

	received_catalogs = fields.Field()
	shared_catalogs = fields.Field()
	received_products = fields.Field()
	opened_products = fields.Field()
	received_7days_products = fields.Field()
	opened_7days_products = fields.Field()

	sales_order = fields.Field()
	purchase_order = fields.Field()
	last_received_catalog = fields.Field()
	company_types = fields.Field()

	class Meta:
		model = User
		skip_unchanged = True
		report_skipped = False
		fields = ('id', 'username', 'user_type', 'company', 'company_types', 'state', 'city', 'invited_by_company', 'invite_type', 'person_name', 'phone', 'last_login', 'date_joined', 'last_received_catalog', 'buyer_approved', 'supplier_approved', 'received_products', 'opened_products', 'received_7days_products', 'opened_7days_products', 'buyer_invited', 'buyer_registered', 'supplier_invited', 'supplier_registered', 'received_catalogs', 'shared_catalogs', 'sales_order', 'purchase_order')
		export_order = ('id', 'username', 'user_type', 'company', 'company_types', 'state', 'city', 'invited_by_company', 'invite_type', 'person_name', 'phone', 'last_login', 'date_joined', 'last_received_catalog', 'buyer_approved', 'supplier_approved', 'received_products', 'opened_products', 'received_7days_products', 'opened_7days_products', 'buyer_invited', 'buyer_registered', 'supplier_invited', 'supplier_registered', 'received_catalogs', 'shared_catalogs', 'sales_order', 'purchase_order')

	def get_queryset(self, request):
	    return super(UserCompanyDetailResource, self).get_queryset(request).select_related('companyuser__company__state', 'companyuser__company__city', 'userprofile', 'companyuser__company__country')

	def dehydrate_person_name(self, obj):
		try:
			fullname = obj.first_name + " " + obj.last_name
			return fullname
		except:
			return ""

	def dehydrate_phone(self, obj):
		try:
			phone = obj.userprofile.phone_number
			return phone
		except:
			return ""

	def dehydrate_is_profile_set(self, obj):
		try:
			is_profile_set = obj.userprofile.is_profile_set
			return is_profile_set
		except:
			return ""

	def dehydrate_company(self, obj):
		try:
			global companyObj
			companyObj = obj.companyuser.company
			return companyObj.name
		except:
			return ""

	def dehydrate_invited_by_company(self, obj):
		try:
			global companyObj

			invitee = Invitee.objects.filter(invitee_number = companyObj.phone_number, country=companyObj.country, invite__time__lte=obj.date_joined+timedelta(hours=12)).select_related('invite__company__city', 'invite__user').first()

			return invitee.invite.company.name

		except:
			return ""

	def dehydrate_invite_type(self, obj):
		try:
			global inviteeObj

			inviteeObj = Invitee.objects.filter(invitee_number = companyObj.phone_number, country=companyObj.country, invite__time__lte=obj.date_joined+timedelta(hours=12)).select_related('invite__company__city', 'invite__user').first()

			return inviteeObj.invitee_id.first().group_type.name

		except:
			return ""

	def dehydrate_state(self, obj):
		try:
			global companyObj
			global address
			address = companyObj.address
			return address.state.state_name
		except:
			return ""

	def dehydrate_city(self, obj):
		try:
			global companyObj
			global address
			return address.city.city_name
		except:
			return ""

	def dehydrate_user_type(self, obj):
		try:
			# ~ name = obj.groups.values_list('name', flat=True)
			# ~ return ', '.join(name)
			names = []
			usergroups = obj.groups.all()
			for usergroup in usergroups:
			    names.append(usergroup.name)
			return ', '.join(names)
		except:
			return ""

	def dehydrate_buyer_invited(self, obj):
		try:
			global companyObj
			return Invitee.objects.filter(invite__company=companyObj, invite__relationship_type="buyer").count()
		except:
			return ""

	def dehydrate_buyer_registered(self, obj):
		try:
			global companyObj
			return Buyer.objects.filter(selling_company=companyObj, buying_company__isnull=False).count()
		except:
			return ""

	def dehydrate_buyer_approved(self, obj):
		try:
			global companyObj
			return Buyer.objects.filter(selling_company=companyObj, status="approved").count()
		except:
			return ""

	def dehydrate_supplier_invited(self, obj):
		try:
			global companyObj
			return Invitee.objects.filter(invite__company=companyObj, invite__relationship_type="supplier").count()
		except:
			return ""

	def dehydrate_supplier_registered(self, obj):
		try:
			global companyObj
			return Buyer.objects.filter(buying_company=companyObj, selling_company__isnull=False).count()
		except:
			return ""

	def dehydrate_supplier_approved(self, obj):
		try:
			global companyObj
			return Buyer.objects.filter(buying_company=companyObj, status="approved").count()
		except:
			return ""

	def dehydrate_received_catalogs(self, obj):
	    try:
		total = Push_User.objects.filter(buying_company=companyObj, catalog__isnull=False).values_list('catalog', flat=True).distinct().count()
		return total
	    except:
		return ""

	def dehydrate_shared_catalogs(self, obj):
	    try:
		total = Push_User.objects.filter(selling_company=companyObj, catalog__isnull=False).values_list('catalog', flat=True).distinct().count()
		return total
	    except:
		return ""

	def dehydrate_received_products(self, obj):
		try:
			#total = Push_User_Product.objects.filter(buying_company=companyObj).values_list('product', flat=True).distinct().count()
			total = CompanyProductFlat.objects.filter(buying_company=companyObj).values_list('product', flat=True).distinct().count()
			return total
		except:
			return ""

	def dehydrate_opened_products(self, obj):
		try:
			#total = Push_User_Product.objects.filter(buying_company=companyObj, is_viewed='yes').values_list('product', flat=True).distinct().count()
			total = CompanyProductFlat.objects.filter(buying_company=companyObj, is_viewed='yes').values_list('product', flat=True).distinct().count()
			return total
		except:
			return ""

	def dehydrate_received_7days_products(self, obj):
		try:
			global last7dayDate
			todayDate = date.today()
			last7dayDate = todayDate - timedelta(days=7)

			#total = Push_User_Product.objects.filter(buying_company=companyObj, push__date__gte=last7dayDate).values_list('product', flat=True).distinct().count()
			total = CompanyProductFlat.objects.filter(buying_company=companyObj, push_reference__date__gte=last7dayDate).values_list('product', flat=True).distinct().count()
			return total
		except:
			return ""

	def dehydrate_opened_7days_products(self, obj):
		try:
			global last7dayDate
			#total = Push_User_Product.objects.filter(buying_company=companyObj, push__date__gte=last7dayDate, is_viewed='yes').values_list('product', flat=True).distinct().count()
			total = CompanyProductFlat.objects.filter(buying_company=companyObj, push_reference__date__gte=last7dayDate, is_viewed='yes').values_list('product', flat=True).distinct().count()
			return total
		except:
			return ""

	def dehydrate_sales_order(self, obj):
		try:
			total = SalesOrder.objects.filter(seller_company=companyObj).values_list('id', flat=True).distinct().count()
			return total
		except:
			return ""

	def dehydrate_purchase_order(self, obj):
		try:
			total = SalesOrder.objects.filter(company=companyObj).values_list('id', flat=True).distinct().count()
			return total
		except:
			return ""

	def dehydrate_last_received_catalog(self, obj):
		try:
			push_id= Push_User.objects.filter(buying_company=companyObj, catalog__isnull=False).values_list('push_id', flat=True).order_by('-push_id')[:1]
			push = Push.objects.filter(pk=push_id[0])

			return push[0].time
		except:
			return ""

	def dehydrate_company_types(self, obj):
		try:
			global companyObj
			ct = CompanyType.objects.get(company=companyObj.id)
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

			return arr
		except:
			return ""

class UserCompanyDetailAdmin(ExportMixin, admin.ModelAdmin):
    inlines = [UserProfileInline, ]
    list_display = ('id', 'username', 'user_type', 'company', 'company_types', 'state', 'city', 'invited_by_company', 'invite_type', 'person_name', 'phone', 'last_login', 'date_joined', 'last_received_catalog', 'buyer_approved', 'supplier_approved', 'received_products', 'opened_products', 'received_7days_products', 'opened_7days_products', 'buyer_invited', 'buyer_registered', 'supplier_invited', 'supplier_registered', 'received_catalogs', 'shared_catalogs', 'sales_order', 'purchase_order')
    list_filter = ('date_joined', 'last_login', UserFilter, ('date_joined', DateRangeFilter), ('last_login', DateRangeFilter))
    search_fields = ('id', 'username', 'companyuser__company__name', 'userprofile__phone_number', 'first_name', 'last_name', 'last_login', 'companyuser__company__address__state__state_name', 'companyuser__company__address__city__city_name', 'date_joined', )
    ordering = ('-id',)
    resource_class = UserCompanyDetailResource
    #list_select_related = ('companyuser__company',)
    #date_hierarchy = 'last_login'
    actions = ['notification_or_sms']

    def get_queryset(self, request):
	return super(UserCompanyDetailAdmin, self).get_queryset(request).select_related('companyuser__company__address__state', 'companyuser__company__address__city', 'userprofile', 'companyuser__company__country', 'companyuser__company__company_group_flag').prefetch_related('groups')

    def notification_or_sms(self, request, queryset):
	if request.POST.get('post'):
	    print "Post"

	    ids = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
	    message_type = request.POST.get('message_type')
	    message = request.POST.get('message')

	    print ids
	    print message_type
	    print message

	    if message_type == "notification":
		rno = random.randrange(100000, 999999, 1)

		image = settings.MEDIA_URL+"logo-single.png"

		if settings.TASK_QUEUE_METHOD == 'celery':
		    notificationSend.apply_async((ids, message, {"notId": rno, "title":"Wishbook", "push_type":"promotional", "image":image}), expires=datetime.now() + timedelta(days=2))
		elif settings.TASK_QUEUE_METHOD == 'djangoQ':
		    task_id = async(
			    'api.tasks.notificationSend',
			    ids, message, {"notId": rno, "title":"Wishbook", "push_type":"promotional", "image":image}
		    )

		'''device = GCMDevice.objects.filter(user__in=ids, active=True)

		logger.info(str(device))

		apnsdevice = APNSDevice.objects.filter(user__in=ids, active=True)

		logger.info(str(apnsdevice))

		rno = random.randrange(100000, 999999, 1)

		image = settings.MEDIA_URL+"logo-single.png"
		if device:
		    try:
			status = device.send_message(message, extra={"notId": rno, "title":"Wishbook", "push_type":"promotional", "image":image})#"notId":pid,"push_type":pushType,"image":pushImage, "company_image":companyImage, "name":text, "table_id": tableId
			logger.info(str(status))
		    except Exception:
			pass

		if apnsdevice:
		    try:
			status = apnsdevice.send_message(message, extra={"notId": rno, "title":"Wishbook", "push_type":"promotional", "image":image})#"notId":pid,"push_type":pushType,"image":pushImage, "company_image":companyImage, "name":text, "table_id": tableId
			logger.info(str(status))
		    except Exception:
			pass'''

	    elif message_type == "sms":
		phone_number = UserProfile.objects.filter(user__in=ids).annotate(phone=Concat('country__phone_code',Value(''),'phone_number')).values_list('phone', flat=True).distinct()
		reqs = []

		'''for number in phone_number:
		    logger.info(str(number))

		    url = smsUrl()% (number)

		    template = smsTemplates("pushPendingBuyer")% ("wishbooks", "catalogs")
		    template = urllib.quote_plus(template)

		    url = url+template

		    res = grequests.get(url)
		    reqs.append(res)

		try:
		    greqs = grequests.map(reqs)
		    logger.info(greqs)
		except Exception:
		    pass'''

	    #messages.success(request, 'Message has been sent to '.format(queryset.count()))
	    #self.message_user(request, "Message has been sent")
	    #return HttpResponseRedirect(request.get_full_path())
	    self.message_user(request, "Message has been sent")
	else:
	    print "Form"

	    context = {
		'title': "Send message using notification or sms",
		'queryset': queryset,
		'action_checkbox_name': helpers.ACTION_CHECKBOX_NAME,
	    }
	    return TemplateResponse(request, 'admin/api/user_company_detail/action_message.html', context, current_app=self.admin_site.name)

    notification_or_sms.short_description = u'Send Notification or SMS'

    def company(self, obj):
	try:
	    global companyObj
	    companyObj = obj.companyuser.company
	    return companyObj.name
	except:
	    return ""
    company.admin_order_field = 'companyuser__company__name'

    def invited_by_company(self, obj):
	try:
	    global companyObj
	    global inviteeObj

	    inviteeObj = Invitee.objects.filter(invitee_number = companyObj.phone_number, country=companyObj.country, invite__time__lte=obj.date_joined+timedelta(hours=12)).select_related('invite__company').first()

	    return inviteeObj.invite.company.name

	except:
	    return ""

    def invite_type(self, obj):
	try:
	    global inviteeObj

	    #inviteeObj = Invitee.objects.filter(invitee_number = companyObj.phone_number, country=companyObj.country, invite__time__lte=obj.date_joined+timedelta(hours=12)).select_related('invite__company__city', 'invite__user').first()

	    return inviteeObj.invitee_id.first().group_type.name

	except:
	    return ""

    def person_name(self, obj):
	try:
	    fullname = obj.first_name + " " + obj.last_name
	    return fullname
	except:
	    return ""
    person_name.admin_order_field = 'first_name'

    def phone(self, obj):
	try:
	    phone = obj.userprofile.phone_number
	    return phone
	    #return '<img border="0" alt="%s" src="%s" width="50" height="50">' % (phone,)
	except:
	    return ""
    phone.allow_tags = True
    phone.admin_order_field = 'userprofile__phone_number'

    def is_profile_set(self, obj):
	try:
	    is_profile_set = obj.userprofile.is_profile_set
	    return is_profile_set
	except:
	    return ""
    is_profile_set.admin_order_field = 'userprofile__phone_number'

    def state(self, obj):
	try:
	    global companyObj
	    global address
	    address = companyObj.address
	    return address.state.state_name
	except:
	    return ""
    state.admin_order_field = 'companyuser__company__state__state_name'

    def city(self, obj):
	try:
	    global companyObj
	    global address
	    return address.city.city_name
	except:
	    return ""
    city.admin_order_field = 'companyuser__company__city__city_name'

    def user_type(self, obj):
	try:
	    # ~ name = obj.groups.values_list('name', flat=True)
	    # ~ return ', '.join(name)
	    names = []
	    usergroups = obj.groups.all()
	    for usergroup in usergroups:
		names.append(usergroup.name)
	    return ', '.join(names)
	except:
	    return ""
    user_type.admin_order_field = 'groups'

    def buyer_invited(self, obj):
	try:
	    global companyObj
	    return Invitee.objects.filter(invite__company=companyObj, invite__relationship_type="buyer").count()
	except:
	    return ""


    def buyer_registered(self, obj):
	try:
	    global companyObj
	    return Buyer.objects.filter(selling_company=companyObj, buying_company__isnull=False).count()
	except:
	    return ""

    def buyer_approved(self, obj):
	try:
	    global companyObj
	    return Buyer.objects.filter(selling_company=companyObj, status="approved").count()
	except:
	    return ""

    def supplier_invited(self, obj):
	try:
	    global companyObj
	    return Invitee.objects.filter(invite__company=companyObj, invite__relationship_type="supplier").count()
	except:
	    return ""

    def supplier_registered(self, obj):
	try:
	    global companyObj
	    return Buyer.objects.filter(buying_company=companyObj, selling_company__isnull=False).count()
	except:
	    return ""

    def supplier_approved(self, obj):
	try:
	    global companyObj
	    return Buyer.objects.filter(buying_company=companyObj, status="approved").count()
	except:
	    return ""

    def received_catalogs(self, obj):
	try:
	    global companyObj
	    total = Push_User.objects.filter(buying_company=companyObj, catalog__isnull=False).values_list('catalog', flat=True).distinct().count()
	    return total
	except:
	    return ""

    def shared_catalogs(self, obj):
	try:
	    global companyObj
	    total = Push_User.objects.filter(selling_company=companyObj, catalog__isnull=False).values_list('catalog', flat=True).distinct().count()
	    return total
	except:
	    return ""

    def received_products(self, obj):
	try:
	    global companyObj
	    #total = Push_User_Product.objects.filter(buying_company=companyObj).values_list('product', flat=True).distinct().count()
	    total = CompanyProductFlat.objects.filter(buying_company=companyObj).values_list('product', flat=True).distinct().count()
	    return total
	except:
	    return ""

    def opened_products(self, obj):
	try:
	    global companyObj
	    #total = Push_User_Product.objects.filter(buying_company=companyObj, is_viewed='yes').values_list('product', flat=True).distinct().count()
	    total = CompanyProductFlat.objects.filter(buying_company=companyObj, is_viewed='yes').values_list('product', flat=True).distinct().count()
	    return total
	except:
	    return ""

    def received_7days_products(self, obj):
	try:
	    global last7dayDate
	    todayDate = date.today()
	    last7dayDate = todayDate - timedelta(days=7)

	    #total = Push_User_Product.objects.filter(buying_company=companyObj, push__date__gte=last7dayDate).values_list('product', flat=True).distinct().count()
	    total = CompanyProductFlat.objects.filter(buying_company=companyObj, push_reference__date__gte=last7dayDate).values_list('product', flat=True).distinct().count()
	    return total
	except:
	    return ""

    def opened_7days_products(self, obj):
	try:
	    global last7dayDate
	    #total = Push_User_Product.objects.filter(buying_company=companyObj, push__date__gte=last7dayDate, is_viewed='yes').values_list('product', flat=True).distinct().count()
	    total = CompanyProductFlat.objects.filter(buying_company=companyObj, push_reference__date__gte=last7dayDate, is_viewed='yes').values_list('product', flat=True).distinct().count()
	    return total
	except:
	    return ""

    def sales_order(self, obj):
	try:
	    global companyObj
	    total = SalesOrder.objects.filter(seller_company=companyObj).values_list('id', flat=True).distinct().count()
	    return total
	except:
	    return ""

    def purchase_order(self, obj):
	try:
	    global companyObj
	    total = SalesOrder.objects.filter(company=companyObj).values_list('id', flat=True).distinct().count()
	    return total
	except:
	    return ""

    def last_received_catalog(self, obj):
	try:
	    push_id= Push_User.objects.filter(buying_company=companyObj, catalog__isnull=False).values_list('push_id', flat=True).order_by('-push_id')[:1]
	    push = Push.objects.filter(pk=push_id[0])

	    return push[0].time
	except:
	    return ""

    def company_types(self, obj):
	try:
	    global companyObj
	    #ct = CompanyType.objects.get(company=companyObj.id)
	    ct = companyObj.company_group_flag
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

	    return arr
	except:
	    return ""

    '''class Media:	#add below js and css files in /static/ folder
	js = ('admin/js/custom.js',)

	css = {
	    'all': ('admin/css/custom.css',)
	}'''

admin.site.register(UserCompanyDetail, UserCompanyDetailAdmin)


BranchForm = select2_modelform(Branch, attrs={'width': '250px'})
class BranchAdmin(admin.ModelAdmin):
	list_display = ('id', 'name', 'company', )
	#list_filter = ('id', 'name', 'company', )
	search_fields = ('id', 'name', 'company__name', )
	raw_id_fields = ('company', 'address')
	#form = BranchForm

	def get_queryset(self, request):
	    return super(BranchAdmin, self).get_queryset(request).select_related('company')

admin.site.register(Branch, BranchAdmin)

CompanyUserForm = select2_modelform(CompanyUser, attrs={'width': '250px'})
class CompanyUserAdmin(admin.ModelAdmin):
	list_display = ('id', 'user', 'user_detail', 'company', 'company_phone_number', 'company_detail', 'deputed_from', 'deputed_to')
	#list_filter = ('company', )
	search_fields = ('id', 'user__username', 'user__userprofile__phone_number', 'user__id', 'company__phone_number', 'company__name', 'company__id', 'deputed_from__name', 'deputed_to__name')
	raw_id_fields = ('company', 'deputed_from', 'user', 'deputed_to')
	readonly_fields = ('created', 'modified',)
	#form = CompanyUserForm

	def get_queryset(self, request):
	    return super(CompanyUserAdmin, self).get_queryset(request).select_related('user', 'company')

	# ~ def userid(self, obj):
	    # ~ try:
		# ~ uid = obj.user.id
		# ~ return uid
	    # ~ except:
		# ~ return ""
	# ~ userid.admin_order_field = 'user__id'

	def user_detail(self, obj):
	    return '<a href="%s" target="_blank">%s</a>' % ("/api/admin/auth/user/"+str(obj.user.id), obj.user.id)
	user_detail.allow_tags = True
	user_detail.short_description = 'User Details'
	user_detail.admin_order_field = 'user__id'

	# ~ def user_phone_number(self, obj):
	    # ~ try:
		# ~ return obj.user.userprofile.phone_number
	    # ~ except:
		# ~ return ""
	# ~ user_phone_number.admin_order_field = 'user__userprofile__phone_number'

	def companyid(self, obj):
	    try:
		cid = obj.company.id
		return cid
	    except:
		return ""
	companyid.admin_order_field = 'company__id'

	def company_phone_number(self, obj):
	    try:
		return obj.company.phone_number
	    except:
		return ""
	company_phone_number.admin_order_field = 'company__phone_number'

	def company_detail(self, obj):
	    return '<a href="%s" target="_blank">%s</a>' % ("/api/admin/api/company/"+str(obj.company.id), obj.company.id)
	company_detail.allow_tags = True
	company_detail.short_description = 'Company Details'
	company_detail.admin_order_field = 'company__id'



admin.site.register(CompanyUser, CompanyUserAdmin)

class BrandResource(resources.ModelResource):
    total_catalog = fields.Field()
    total_public_catalogs = fields.Field()

    class Meta:
	    model = Brand
	    skip_unchanged = True
	    report_skipped = False
	    fields = ('id', 'name', 'manufacturer_company__name', 'company__name', 'total_catalog', 'total_public_catalogs')
	    export_order = ('id', 'name', 'manufacturer_company__name', 'company__name', 'total_catalog', 'total_public_catalogs')

    def get_queryset(self, request):
	    return super(BrandResource, self).get_queryset(request).select_related('manufacturer_company', 'company')

    def dehydrate_total_catalog(self, obj):
	    try:
		    return Catalog.objects.filter(brand=obj).count()
	    except:
		    return ""

    def dehydrate_total_public_catalogs(self, obj):
	    return obj.total_catalog

BrandForm = select2_modelform(Brand, attrs={'width': '250px'})
class BrandAdmin(ExportMixin, admin.ModelAdmin):
	list_display = ('id', 'name', 'manufacturer_company', 'company', 'total_catalogs', 'total_public_catalogs', )#'brandimage',
	search_fields = ('id', 'name', 'manufacturer_company__name', 'company__name', 'total_catalog',)
	raw_id_fields = ('manufacturer_company', 'company', 'user')
	#form = BrandForm
	resource_class = BrandResource
	readonly_fields = ('created', 'modified',)

	def get_queryset(self, request):
	    return super(BrandAdmin, self).get_queryset(request).select_related('manufacturer_company', 'company').prefetch_related('catalog_set')

	def brandimage(self, obj):
	    return '<img border="0" alt="%s" src="%s" width="50" height="50">' % (obj.name, obj.image.thumbnail[settings.SMALL_SQR_IMAGE].url,)
	brandimage.allow_tags = True
	brandimage.short_description = 'Brand Image'

	def total_catalogs(self, obj):
	    try:
		#return Catalog.objects.filter(brand=obj).count()
		return obj.catalog_set.count()
	    except:
		return ""

	def total_public_catalogs(self, obj):
	    return obj.total_catalog

admin.site.register(Brand, BrandAdmin)

BrandDistributorForm = select2_modelform(BrandDistributor, attrs={'width': '250px'})
class BrandDistributorAdmin(admin.ModelAdmin):
	list_display = ('id', 'company', )
	#list_filter = ('id', 'company', )
	search_fields = ('id', 'company__name', )
	filter_horizontal = ('brand',)
	raw_id_fields = ('company',)
	form = BrandDistributorForm
	readonly_fields = ('created', 'modified',)

	def get_queryset(self, request):
	    return super(BrandDistributorAdmin, self).get_queryset(request).select_related('company')

admin.site.register(BrandDistributor, BrandDistributorAdmin)
from django.utils import formats
from django.utils.formats import date_format

class CatalogResource(resources.ModelResource):
	total_products = fields.Field()
	total_product_price = fields.Field()
	view_count = fields.Field()
	#created_at_date = fields.Field()
	class Meta:
		model = Catalog
		skip_unchanged = True
		report_skipped = False
		fields = ('id', 'title', 'brand__name', 'view_permission', 'company__name','company__phone_number', 'total_products', 'total_product_price', 'view_count', 'created_at', 'expiry_date', 'supplier_disabled', 'deleted',)
		export_order = ('id', 'title', 'brand__name', 'view_permission', 'company__name','company__phone_number', 'total_products', 'total_product_price', 'view_count', 'created_at', 'expiry_date', 'supplier_disabled', 'deleted',)
		widgets = {
		    'created_at': {'format': '%B %d, %Y'},
                }

	def dehydrate_total_products(self, obj):
		return Product.objects.filter(catalog=obj).count()

	def dehydrate_total_product_price(self, obj):
		price = Product.objects.filter(catalog=obj).aggregate(Sum('price')).get('price__sum', 0)
		if price is None:
			price = 0
		return price

	def dehydrate_view_count(self, obj):
		return CompanyCatalogView.objects.filter(catalog=obj).count()

	'''def dehydrate_created_at_date(self, obj):
		try:
			print obj.created_at

			return obj.created_at
			timezone.localtime(user.last_login).strftime("%B %d, %Y, %I:%M%p")
		except:
			return ''
	'''

class ProductInline(admin.TabularInline):
    model = Product
    extra = 0
    max_num = 0
    can_delete = False
    show_change_link = True
    raw_id_fields = ('catalog', 'mirror', 'user')
    exclude = ['image', 'fabric', 'work', 'user', 'is_hidden', 'box_volumetric_dimension', 'weight']

CatalogForm = select2_modelform(Catalog, attrs={'width': '250px'})
class CatalogAdmin(ExportMixin, admin.ModelAdmin):
	list_display = ('id', 'title', 'brand', 'view_permission', 'company_detail', 'total_products', 'view_count', 'created_at', 'expiry_date', 'supplier_disabled', 'deleted')#,'old_expiry_date')#'catalogimage',
	list_filter = ('view_permission', 'deleted', 'supplier_disabled', ('created_at', DateRangeFilter), ('expiry_date', DateRangeFilter))
	search_fields = ('id', 'title', 'brand__name', 'company__name')
	#filter_horizontal = ('category',)
	raw_id_fields = ('brand', 'category', 'company', 'mirror', 'user')
	#form = CatalogForm
	actions = ['soft_delete']
	resource_class = CatalogResource
	readonly_fields = ('created_at', 'modified',)
	inlines = (ProductInline, )

	def save_model(self, request, obj, form, change):
	    obj.save()
	    catalogEAVset(obj)

	def get_queryset(self, request):
		qs = self.model._default_manager.all_with_deleted().select_related('brand', 'company').prefetch_related('products', 'companycatalogview_set')
		ordering = self.ordering or () # otherwise we might try to *None, which is bad ;)
		if ordering:
			qs = qs.order_by(*ordering)
		return qs

	def soft_delete(self, request, queryset):
	    queryset.update(deleted=True)
	    messages.success(request, 'Selected catalogs have been soft deleted')
	    return

	def catalogimage(self, obj):
	    return '<img border="0" alt="%s" src="%s" width="50" height="50">' % (obj.title, obj.thumbnail.thumbnail[settings.SMALL_IMAGE].url,)

	def total_products(self, obj):
	    #return Product.objects.filter(catalog=obj).count()
	    return obj.products.count()

	def view_count(self, obj):
	    #return CompanyCatalogView.objects.filter(catalog=obj).count()
	    return obj.companycatalogview_set.count()

	catalogimage.allow_tags = True
	catalogimage.short_description = 'Catalog Image'

	def company_detail(self, obj):
		if obj.company:
			return '<a href="%s" target="_blank">%s</a>' % ("/api/admin/api/company/"+str(obj.company.id), obj.company)
		return None
	company_detail.allow_tags = True
	company_detail.short_description = 'Company'
	company_detail.admin_order_field = 'company_id'

admin.site.register(Catalog, CatalogAdmin)


class ProductResource(resources.ModelResource):
	class Meta:
		model = Product
		skip_unchanged = True
		report_skipped = False
		fields = ('id', 'title', 'sku', 'price', 'public_price', 'catalog__title', 'catalog__brand__name', 'catalog__company__name', 'created_at')
		export_order = ('id', 'title', 'sku', 'price', 'public_price', 'catalog__title', 'catalog__brand__name', 'catalog__company__name', 'created_at')
		widgets = {
		    'created_at': {'format': '%B %d, %Y'},
                }


class ProductAdminForm(BaseDynamicEntityForm):
    model = Product

    Meta = select2_modelform_meta(Product)

#class ProductAdmin(BaseEntityAdmin):
#	form = ProductAdminForm
#class ProductAdmin(admin.ModelAdmin):
ProductForm = select2_modelform(Product, attrs={'width': '250px'})
class ProductAdmin(ExportMixin, admin.ModelAdmin):#BaseEntityAdmin
	#form = ProductAdminForm
	list_display = ('id', 'title', 'price', 'public_price', 'catalog_detail', 'brand', 'company', 'created_at', 'deleted',)#'productimage',
	list_filter = ('deleted', ('created_at', DateRangeFilter))
	search_fields = ('id', 'title', 'price', 'public_price', 'catalog__title', 'catalog__brand__name', 'catalog__company__name')
	#filter_horizontal = ('catalog', )
	raw_id_fields = ('catalog', 'mirror', 'user')
	#form = ProductAdminForm #ProductForm#ProductAdminForm #
	resource_class = ProductResource
	readonly_fields = ('created_at', 'modified',)

	def productimage(self, obj):
	    return '<img border="0" alt="%s" src="%s" width="50" height="50">' % (obj.title, obj.image.thumbnail[settings.SMALL_IMAGE].url,)
	productimage.allow_tags = True
	productimage.short_description = 'Product Image'

	def get_queryset(self, request):
		qs = self.model._default_manager.all_with_deleted().select_related('catalog__brand', 'catalog__company')
		ordering = self.ordering or () # otherwise we might try to *None, which is bad ;)
		if ordering:
			qs = qs.order_by(*ordering)
		return qs

	'''def catalogs(self, obj):
	    try:
		title = obj.catalog.all().values_list('title', flat=True).distinct()
		return ', '.join(title)
	    except:
		return ""'''

	def company(self, obj):
	    try:
		return obj.catalog.company.name
	    except:
		return ""

	def brand(self, obj):
	    try:
		return obj.catalog.brand.name
	    except:
		return ""

	def catalog_detail(self, obj):
		if obj.catalog:
			return '<a href="%s" target="_blank">%s</a>' % ("/api/admin/api/catalog/"+str(obj.catalog.id), obj.catalog)
		return None
	catalog_detail.allow_tags = True
	catalog_detail.short_description = 'Catalog'
	catalog_detail.admin_order_field = 'catalogy_id'

admin.site.register(Product, ProductAdmin)

'''CatalogListForm = select2_modelform(CatalogList, attrs={'width': '250px'})
class CatalogListAdmin(admin.ModelAdmin):
	list_display = ('id', 'name', 'user',)
	#list_filter = ('id', 'company', )
	search_fields = ('id', 'name', 'user__username',)
	filter_horizontal = ('catalogs', )
	form = CatalogListForm

	def get_queryset(self, request):
	    return super(CatalogListAdmin, self).get_queryset(request).select_related('user')

admin.site.register(CatalogList, CatalogListAdmin)'''


from django.contrib import messages
'''from django.shortcuts import render
from django import forms
class CatalogForm(forms.Form):
    catalog = forms.ModelChoiceField(queryset=Catalog.objects.all())'''

class BuyerResource(resources.ModelResource):
	invite_date = fields.Field()
	last_login = fields.Field()
	enquiry_catalog_name = fields.Field()
	class Meta:
		model = Buyer
		skip_unchanged = True
		report_skipped = False
		fields = ('id', 'selling_company__name', 'buying_company__name', 'selling_company__phone_number', 'buying_company__phone_number', 'status', 'group_type__name', 'invitee__invitee_number', 'invitee__invitation_type', 'invite_date', 'last_login', 'enquiry_catalog_name')
		export_order = ('id', 'selling_company__name', 'buying_company__name', 'selling_company__phone_number', 'buying_company__phone_number', 'status', 'group_type__name', 'invitee__invitee_number', 'invitee__invitation_type', 'invite_date', 'last_login', 'enquiry_catalog_name')

	def get_queryset(self, request):
		return super(BuyerResource, self).get_queryset(request).select_related('selling_company', 'buying_company', 'group_type','invitee__invite', 'buying_company__chat_admin_user')

	def dehydrate_invite_date(self, obj):
		try:
		    invitedate = obj.invitee.invite.date
		    return invitedate
		except:
		    return ""

	def dehydrate_last_login(self, obj):
		try:
		    user = CompanyUser.objects.filter(company=obj.buying_company).first().user
		    return timezone.localtime(user.last_login).strftime("%B %d, %Y, %I:%M%p")
		except:
		    return ""

	def dehydrate_enquiry_catalog_name(self, obj):
		try:
		    if obj.enquiry_catalog:
			return obj.enquiry_catalog.title
		    else:
			return ""
		except:
		    return ""


BuyerForm = select2_modelform(Buyer, attrs={'width': '250px'})
class BuyerAdmin(ExportMixin, admin.ModelAdmin):
	list_display = ('id', 'selling_compny', 'buying_compny', 'status', 'buyer_type', 'created_type', 'group_type', 'invitee_number', 'invite_date', 'invitation_type', 'user', 'created_at', 'buyer_last_login')
	list_filter = ('status', 'buyer_type', 'created_type', 'invitee__invitation_type', 'group_type', ('invitee__invite__date', DateRangeFilter), ('created_at', DateRangeFilter))
	search_fields = ('id', 'selling_company__name', 'buying_company__name', 'invitee__invitee_number', 'user__username')
	#list_editable = ("status",)
	resource_class = BuyerResource
	raw_id_fields = ('selling_company', 'buying_company', 'invitee', 'group_type', 'broker_company', 'warehouse', 'preferred_logistics', 'user', 'enquiry_catalog')
	#form = BuyerForm
	actions = ['share', 'approve', 'resend_sms']#,'share_catalog'
	readonly_fields = ('created_at', 'modified',)

	def get_queryset(self, request):
	    return super(BuyerAdmin, self).get_queryset(request).select_related('selling_company', 'buying_company', 'group_type','invitee__invite', 'buying_company__chat_admin_user', 'user')

	def resend_sms(self, request, queryset):
	    ids = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
	    print ids
	    buyers = Buyer.objects.filter(id__in=ids)
	    for buyer in buyers:
		'''if buyer.status == "buyer_registrationpending":
			sendInvite(buyer.invitee.country.phone_code+buyer.invitee.invitee_number, str(buyer.selling_company.name))
		elif buyer.status == "buyer_pending":
			requestNotification(buyer.selling_company, buyer.buying_company.country.phone_code+buyer.buying_company.phone_number, "buyer", buyer, buyer.buying_company, buyer.status)
		elif buyer.status == "supplier_registrationpending":
			sendInvite(buyer.invitee.country.phone_code+buyer.invitee.invitee_number, str(buyer.buying_company.name))
		elif buyer.status == "supplier_pending":
			requestNotification(buyer.buying_company, buyer.buying_company.country.phone_code+buyer.buying_company.phone_number, "supplier", buyer, buyer.selling_company, buyer.status)
		'''
		try:
		    if buyer.invitee.invitation_type == "Buyer":
			requestNotification(buyer.selling_company, buyer.buying_company.country.phone_code+buyer.buying_company.phone_number, "buyer", buyer, buyer.buying_company, buyer.status, False)
		    elif buyer.invitee.invitation_type == "Supplier":
			requestNotification(buyer.buying_company, buyer.buying_company.country.phone_code+buyer.buying_company.phone_number, "supplier", buyer, buyer.selling_company, buyer.status, False)
		except Exception:
		    pass

	    messages.success(request, 'Resent successfully')
	    return

	resend_sms.short_description = u'Resend SMS'

	def approve(self, request, queryset):
	    ids = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
	    print ids
	    buyers = Buyer.objects.filter(id__in=ids)
	    for buyer in buyers:
		if buyer.status == "buyer_pending" or buyer.status == "supplier_pending":
		    buyer.status = "approved"
		    buyer.save()
		    try:
			shareOnApproves(buyer.selling_company, buyer.buying_company)
		    except Exception:
			pass
	    messages.success(request, 'Bulk approved and shared successfully')
	    return
	approve.short_description = u'Bulk approve and share to buyers'

	def share(self, request, queryset):
	    ids = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
	    print ids
	    buyers = Buyer.objects.filter(id__in=ids)
	    for buyer in buyers:
		if buyer.status == "approved":
		    shareOnApproves(buyer.selling_company, buyer.buying_company)
	    messages.success(request, 'shared successfully')
	    return
	share.short_description = u'Share last 7 from supllier to buyer'

	'''def share_catalog(self, request, queryset):
	    if 'do_action' in request.POST:
		form = CatalogForm(request.POST)
		if form.is_valid():
		    catalog = form.cleaned_data['catalog']
		    #updated = queryset.update(catalog=catalog)
		    #messages.success(request, '{0} movies were updated'.format(updated))
		    messages.success(request, '{0} movies were updated'.format(2))
		    return
	    else:
		print ids
		print len(ids)
		if len(ids) > 1:
		    messages.error(request, 'Can not share from multiple company')
		    return

		form = CatalogForm()
		ids = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
		buyers = Buyer.objects.filter(id__in=ids)
		for buyer in buyers:
		    if buyer.status == "approved":
			queryset=Catalog.objects.filter(company=buyer.selling_company)
		    else:
			queryset=Catalog.objects.none()

	    return render(request, 'admin/api/buyer/action_catalog.html',
		{'title': u'Choose catalog',
		 'objects': queryset,
		 'form': form})
	share_catalog.short_description = u'Share catalog'
	'''

	def invitation_type(self, obj):
	    try:
		invitation_type = obj.invitee.invitation_type
		return invitation_type
	    except:
		return ""

	def invite_date(self, obj):
	    try:
		invitedate = obj.invitee.invite.date
		return invitedate
	    except:
		return ""
	def invitee_number(self, obj):
	    try:
		invitee_number = obj.invitee.invitee_number
		return invitee_number
	    except:
		return ""
	invitee_number.admin_order_field = 'invitee__invitee_number'

	def buyer_last_login(self, obj):
	    try:
		#user = CompanyUser.objects.filter(company=obj.buying_company).first().user
		user = obj.buying_company.chat_admin_user
		return timezone.localtime(user.last_login).strftime("%B %d, %Y, %I:%M%p")
	    except:
		return ''

	def selling_compny(self, obj):
		if obj.selling_company:
			return '<a href="%s" target="_blank">%s</a>' % ("/api/admin/api/company/"+str(obj.selling_company.id), obj.selling_company)
		return None
	selling_compny.allow_tags = True
	selling_compny.short_description = 'Selling Company'
	selling_compny.admin_order_field = 'selling_company_id'

	def buying_compny(self, obj):
		if obj.buying_company:
			return '<a href="%s" target="_blank">%s</a>' % ("/api/admin/api/company/"+str(obj.buying_company.id), obj.buying_company)
		return None
	buying_compny.allow_tags = True
	buying_compny.short_description = 'Buying Company'
	buying_compny.admin_order_field = 'buying_company__id'

admin.site.register(Buyer, BuyerAdmin)

class SalesOrderResource(resources.ModelResource):
    total_rate = fields.Field()
    person_name = fields.Field()
    city = fields.Field()
    state = fields.Field()
    payment_status = fields.Field()
    invoice_shipping_charges = fields.Field()
    invoice_total_amt = fields.Field()
    payment_methods = fields.Field()
    payment_date = fields.Field()

    seller_city = fields.Field()
    created_date = fields.Field()
    updated_date = fields.Field()

    class Meta:
	    model = SalesOrder
	    skip_unchanged = True
	    report_skipped = False
	    fields = ('id', 'order_number', 'user__username', 'person_name', 'seller_company__id', 'seller_city', 'seller_company__name', 'company__name', 'company__id', 'city', 'state', 'created_date', 'updated_date', 'processing_status', 'payment_status', 'payment_methods', 'payment_date', 'dispatch_date', 'total_rate', 'invoice_shipping_charges', 'invoice_total_amt', 'supplier_cancel', 'buyer_cancel')
	    export_order = ('id', 'order_number', 'user__username', 'person_name', 'seller_company__id', 'seller_city', 'seller_company__name', 'company__name', 'company__id', 'city', 'state', 'created_date', 'updated_date', 'processing_status', 'payment_status', 'payment_methods', 'payment_date', 'dispatch_date', 'total_rate', 'invoice_shipping_charges', 'invoice_total_amt', 'supplier_cancel', 'buyer_cancel')

    def get_queryset(self, request):
	    #return super(SalesOrderResource, self).get_queryset(request).select_related('user', 'seller_company', 'company__city', 'company__state').prefetch_related('items')
	    return super(SalesOrderResource, self).get_queryset(request).select_related('user', 'seller_company__city', 'ship_to__city', 'ship_to__state').prefetch_related('items')

    def dehydrate_payment_status(self, obj):
	try:
		return obj.payment_status()
	except:
		return ""

    def dehydrate_total_rate(self, obj):
	try:
		return obj.total_rate()
	except:
		return ''

    def dehydrate_person_name(self, obj):
	try:
	    global userObj
	    userObj = obj.user
	    fullname = userObj.first_name + " " + userObj.last_name
	    return fullname
	except:
	    return ""

    def dehydrate_seller_city(self, obj):
	try:
	    return obj.seller_company.city.city_name
	except:
	    return ""

    def dehydrate_city(self, obj):
	try:
	    global companyObj
	    global address
	    address = obj.ship_to
	    return address.city.city_name
	except:
	    return ""

    def dehydrate_state(self, obj):
	try:
	    global companyObj
	    global address
	    return address.state.state_name
	except:
	    return ""

    def dehydrate_invoice_shipping_charges(self, obj):
	try:
	    total = Invoice.objects.filter(order=obj).aggregate(Sum('shipping_charges')).get('shipping_charges__sum', 0)
	    if total is None:
		total = 0
	    return total
	except:
	    return ""

    def dehydrate_invoice_total_amt(self, obj):# shipping_charges+taxes+shipping_charges-discount
	try:
	    total = Invoice.objects.filter(order=obj).aggregate(Sum('total_amount')).get('total_amount__sum', 0)
	    if total is None:
		total = 0
	    return total
	except:
	    return ""

    def dehydrate_payment_methods(self, obj):
	try:
	    methods = []
	    invoces = obj.invoice_set.all()
	    for inv in invoces:
		payments = inv.payments.all()
		for payment in payments:
		    if payment.mode not in methods:
			methods.append(payment.mode)
	    return ", ".join(methods)
	except:
	    return ""

    def dehydrate_payment_date(self, obj):
	try:
	    dates = []
	    invoces = obj.invoice_set.all()
	    for inv in invoces:
		payments = inv.payments.all()
		for payment in payments:
		    dates.append(payment.datetime)
	    return ", ".join(dates)
	except:
	    return ""

    def dehydrate_created_date(self, obj):
		try:
			return timezone.localtime(obj.created_at).strftime("%Y-%m-%d %H:%M:%S") #.strftime("%B %d, %Y, %I:%M%p")
		except:
			return ''

    def dehydrate_updated_date(self, obj):
		try:
			return timezone.localtime(obj.time).strftime("%Y-%m-%d %H:%M:%S") #.strftime("%B %d, %Y, %I:%M%p")
		except:
			return ''



class SalesOrderFilter(SimpleListFilter):
    title = 'payment status' # or use _('country') for translated title
    parameter_name = 'payment_status'

    def lookups(self, request, model_admin):
        return (
            ('Pending', 'Pending'),
            ('Paid', 'Paid'),
            ('Partially Paid', 'Partially Paid'),
            ('Paid or Partially Paid', 'Paid or Partially Paid'),
        )

    def queryset(self, request, queryset):
		if self.value():
			return filterOrderPaymentStatus(queryset, self.value())

SalesOrderItemInlineForm = select2_modelform(SalesOrderItem, attrs={'width': '250px'})
class SalesOrderItemInline(admin.TabularInline):
    model = SalesOrderItem
    extra = 1
    show_change_link = True
    #form = SalesOrderItemInlineForm
    raw_id_fields = ('product',)

class InvoiceInline(admin.TabularInline):
    model = Invoice
    extra = 1
    show_change_link = True
    raw_id_fields = ('wb_coupon',)

SalesOrderForm = select2_modelform(SalesOrder, attrs={'width': '250px'})
class SalesOrderAdmin(ExportMixin, admin.ModelAdmin):
	list_display = ('id', 'order_number', 'user_detail', 'person_name', 'selling_company', 'buying_company', 'city', 'state', 'order_type', 'created_at', 'processing_status', 'payment_status', 'payment_methods', 'payment_date', 'dispatch_date', 'total_rate', 'invoice_shipping_charges', 'invoice_total_amt', 'supplier_cancel', 'buyer_cancel', 'time', 'created_by', 'modified_by')
	list_filter = ('processing_status', 'order_type','source_type', SalesOrderFilter, ('created_at', DateRangeFilter), ('dispatch_date', DateRangeFilter), ('payment_date', DateRangeFilter),  )
	search_fields = ('id', 'order_number', 'user__username', 'user__first_name', 'user__last_name', 'seller_company__name', 'company__name', 'ship_to__city__city_name', 'ship_to__state__state_name', 'order_type', 'processing_status')
	raw_id_fields = ('user', 'seller_company', 'company', 'broker_company', 'backorders', 'tranferred_to', 'ship_to', 'cart')
	#form = SalesOrderForm
	resource_class = SalesOrderResource

	inlines = (InvoiceInline, SalesOrderItemInline)
	readonly_fields = ('created_at', 'time', 'date')

	def get_queryset(self, request):
	    return super(SalesOrderAdmin, self).get_queryset(request).select_related('user', 'seller_company', 'company', 'ship_to__city', 'ship_to__state', 'created_by', 'modified_by').prefetch_related('items', 'invoice_set__payments')

	def user_detail(self, obj):
	    return '<a href="%s" target="_blank">%s</a>' % ("/api/admin/auth/user/"+str(obj.user.id), obj.user)
	user_detail.allow_tags = True
	user_detail.short_description = 'User Details'
	user_detail.admin_order_field = 'user__id'

	def selling_company(self, obj):
	    return '<a href="%s" target="_blank">%s</a>' % ("/api/admin/api/company/"+str(obj.seller_company.id), obj.seller_company)
	selling_company.allow_tags = True
	selling_company.short_description = 'Selling Company'
	selling_company.admin_order_field = 'seller_company_id'

	def buying_company(self, obj):
	    return '<a href="%s" target="_blank">%s</a>' % ("/api/admin/api/company/"+str(obj.company.id), obj.company)
	buying_company.allow_tags = True
	buying_company.short_description = 'Buying Company'
	buying_company.admin_order_field = 'company__id'

	def payment_status(self, obj):
	    try:
		return obj.payment_status()
	    except:
		return ""

	def person_name(self, obj):
	    try:
		global userObj
		userObj = obj.user
		fullname = userObj.first_name + " " + userObj.last_name
		return fullname
	    except:
		return ""
	person_name.admin_order_field = 'user'

	def city(self, obj):
	    try:
		global companyObj
		global address
		address = obj.ship_to
		return address.city.city_name
	    except:
		return ""

	def state(self, obj):
	    try:
		global companyObj
		global address
		return address.state.state_name
	    except:
		return ""

	def invoice_shipping_charges(self, obj):
	    try:
		# ~ total = Invoice.objects.filter(order=obj).aggregate(Sum('shipping_charges')).get('shipping_charges__sum', 0)
		# ~ if total is None:
		    # ~ total = 0
		#global invoces
		total = 0
		invoces = obj.invoice_set.all()
		for inv in invoces:
		    if inv.shipping_charges:
			total += inv.shipping_charges
		return total
	    except:
		return ""

	def invoice_total_amt(self, obj):# shipping_charges+taxes+shipping_charges-discount
	    try:
		# ~ total = Invoice.objects.filter(order=obj).aggregate(Sum('total_amount')).get('total_amount__sum', 0)
		# ~ if total is None:
		    # ~ total = 0
		#global invoces
		total = 0
		invoces = obj.invoice_set.all()
		for inv in invoces:
		    if inv.total_amount:
			total += inv.total_amount
		return total
	    except:
		return ""

	def payment_methods(self, obj):
	    try:
		methods = []
		invoces = obj.invoice_set.all()
		for inv in invoces:
		    payments = inv.payments.all()
		    for payment in payments:
			if payment.mode not in methods:
			    methods.append(payment.mode)
		return ", ".join(methods)
	    except:
		return ""

	def payment_date(self, obj):
	    try:
		dates = []
		invoces = obj.invoice_set.all()
		for inv in invoces:
		    payments = inv.payments.all()
		    for payment in payments:
			dates.append(payment.datetime)
		return ", ".join(dates)
	    except:
		return ""




admin.site.register(SalesOrder, SalesOrderAdmin)


class ApiSalesorderauditlogentryAdmin(admin.ModelAdmin):
	list_display = ('id', 'order_number', 'processing_status', 'created_by', 'modified_by', 'action_type', 'action_user', 'action_date')
	list_filter = ('processing_status', ('created_by', DateRangeFilter), ('modified_by', DateRangeFilter), ('action_date', DateRangeFilter) )
	search_fields = ('id', 'order_number', 'processing_status', 'action_type', 'created_by__username', 'modified_by__username', 'action_user__username')
	raw_id_fields = ('user', 'seller_company', 'company', 'broker_company', 'tranferred_to', 'ship_to', 'action_user', 'created_by', 'modified_by', 'cart')

	def get_queryset(self, request):
	    return super(ApiSalesorderauditlogentryAdmin, self).get_queryset(request).select_related('action_user', 'created_by', 'modified_by')

	#def get_queryset(self, request):
	#    return super(SalesOrderAdmin, self).get_queryset(request).select_related('user', 'seller_company', 'ship_to__city', 'ship_to__state').prefetch_related('items', 'invoice_set__payments')

admin.site.register(ApiSalesorderauditlogentry, ApiSalesorderauditlogentryAdmin)

class SalesOrderItemResource(resources.ModelResource):
    class Meta:
	    model = SalesOrderItem
	    skip_unchanged = True
	    report_skipped = False
	    fields = ('id', 'sales_order__order_number', 'product__id', 'product__sku', 'product__catalog__id', 'product__catalog__title', 'quantity', 'rate', 'pending_quantity', 'invoiced_qty', 'dispatched_qty', 'canceled_qty', 'packing_type', 'note')
	    export_order = ('id', 'sales_order__order_number', 'product__id', 'product__sku', 'product__catalog__id', 'product__catalog__title', 'quantity', 'rate', 'pending_quantity', 'invoiced_qty', 'dispatched_qty', 'canceled_qty', 'packing_type', 'note')

    def get_queryset(self, request):
	    return super(SalesOrderItemResource, self).get_queryset(request).select_related('sales_order', 'product')


SalesOrderItemForm = select2_modelform(SalesOrderItem, attrs={'width': '250px'})
class SalesOrderItemAdmin(ExportMixin, admin.ModelAdmin):
	list_display = ('id', 'order_number', 'product', 'quantity', 'rate', )
	list_filter = ('quantity', )
	search_fields = ('id', 'sales_order__order_number', 'product__title', 'quantity', 'rate',)
	raw_id_fields = ('sales_order', 'product',)
	#form = SalesOrderItemForm
	resource_class = SalesOrderItemResource

	def get_queryset(self, request):
	    return super(SalesOrderItemAdmin, self).get_queryset(request).select_related('sales_order', 'product')

	def order_number(self, obj):
	    try:
		order_number = obj.sales_order.order_number
		return order_number
	    except:
		return ""
	order_number.admin_order_field = 'sales_order__order_number'

admin.site.register(SalesOrderItem, SalesOrderItemAdmin)

SelectionForm = select2_modelform(Selection, attrs={'width': '250px'})
class SelectionAdmin(admin.ModelAdmin):
	list_display = ('id', 'name', 'user', 'deleted',)
	list_filter = ('deleted',)
	search_fields = ('id', 'name', 'user__username', )
	filter_horizontal = ('products', )
	raw_id_fields = ('user', 'products')
	#form = SelectionForm

	def get_queryset(self, request):
	    return super(SelectionAdmin, self).get_queryset(request).select_related('user')

admin.site.register(Selection, SelectionAdmin)

###admin.site.register(ChannelType)
###admin.site.register(Channel)

class PushResource(resources.ModelResource):

    class Meta:
	    model = Push
	    skip_unchanged = True
	    report_skipped = False
	    fields = ('id', 'message', 'buyer_segmentation__segmentation_name', 'single_company_push__name', 'company__name', 'user__username', 'to_show', 'time', 'push_downstream', 'shared_catalog' )
	    export_order = ('id', 'message', 'buyer_segmentation__segmentation_name', 'single_company_push__name', 'company__name', 'user__username', 'to_show', 'time', 'push_downstream', 'shared_catalog')

    def get_queryset(self, request):
	    return super(PushResource, self).get_queryset(request).select_related('buyer_segmentation', 'single_company_push', 'company', 'user', 'shared_catalog')


PushForm = select2_modelform(Push, attrs={'width': '250px'})
class PushAdmin(ExportMixin, admin.ModelAdmin):
	list_display = ('id', 'message', 'buyer_segmentation', 'single_company_push', 'company', 'user', 'to_show', 'time', 'push_downstream', 'shared_catalog')#'catalog', 'selection',
	list_filter = ('to_show', 'push_downstream', ('time', DateRangeFilter))
	search_fields = ('id', 'message', 'buyer_segmentation__segmentation_name', 'single_company_push__name', 'company__name', 'user__username', 'shared_catalog__title',)
	#form = PushForm
	raw_id_fields = ('buyer_segmentation', 'single_company_push', 'user', 'company', 'shared_catalog')
	resource_class = PushResource

	def get_queryset(self, request):
	    return super(PushAdmin, self).get_queryset(request).select_related('buyer_segmentation', 'single_company_push', 'company', 'user', 'shared_catalog')

	# ~ def catalog(self, obj):
	    # ~ try:
		# ~ name = Push_User.objects.filter(push=obj.id).values_list('catalog__title', flat=True).first()
		# ~ return name
	    # ~ except:
		# ~ return ""

	# ~ def selection(self, obj):
	    # ~ try:
		# ~ name = Push_User.objects.filter(push=obj.id).values_list('selection__name', flat=True).first()
		# ~ return name
	    # ~ except:
		# ~ return ""

admin.site.register(Push, PushAdmin)


from django.db.models import Count

class Push_UserResource(resources.ModelResource):
	pushed_products = fields.Field()
	viewed_products = fields.Field()

	class Meta:
		model = Push_User
		skip_unchanged = True
		report_skipped = False
		fields = ('id', 'user__username', 'selling_company__name', 'buying_company__name', 'selection__name', 'catalog__title', 'is_viewed', 'pushed_products', 'viewed_products', 'total_price', 'selling_price',)
		export_order = ('id', 'user__username', 'selling_company__name', 'buying_company__name', 'selection__name', 'catalog__title', 'is_viewed', 'pushed_products', 'viewed_products', 'total_price', 'selling_price',)

	def dehydrate_pushed_products(self, obj):
		try:
			#return Push_User_Product.objects.filter(user=obj.user, catalog=obj.catalog, selection=obj.selection, push=obj.push).count()
			return CompanyProductFlat.objects.filter(buying_company=obj.buying_company, catalog=obj.catalog, selection=obj.selection, push_reference=obj.push).count()
		except:
			return ""

	def dehydrate_viewed_products(self, obj):
		try:
			#return Push_User_Product.objects.filter(user=obj.user, catalog=obj.catalog, selection=obj.selection, push=obj.push, is_viewed="yes").count()
			return CompanyProductFlat.objects.filter(buying_company=obj.buying_company, catalog=obj.catalog, selection=obj.selection, push_reference=obj.push, is_viewed="yes").count()
		except:
			return ""

Push_UserForm = select2_modelform(Push_User, attrs={'width': '250px'})
class Push_UserAdmin(ExportMixin, admin.ModelAdmin):
	list_display = ('id', 'push_fuction', 'selling_company', 'buying_company', 'selection', 'catalog', 'is_viewed', 'total_price', 'selling_price', 'expiry_date', 'supplier_disabled', 'buyer_disabled', 'deleted',)#'pushed_products', 'viewed_products',
	list_filter = ('deleted', 'is_viewed', 'supplier_disabled', 'buyer_disabled', ('push__time', DateRangeFilter), ('expiry_date', DateRangeFilter))
	search_fields = ('id', 'push__id', 'selling_company__name', 'buying_company__name', 'selection__name', 'catalog__title', 'total_price', 'selling_price')
	#form = Push_UserForm
	resource_class = Push_UserResource
	raw_id_fields = ('push', 'user', 'selection', 'catalog', 'selling_company', 'buying_company')

	def get_queryset(self, request):
	    qs = self.model._default_manager.all_with_deleted().select_related('push', 'selling_company', 'buying_company', 'selection', 'catalog')
	    #.extra(
	    #select={'pushed_products': 'select count(*) from `api_push_user_product` where `api_push_user_product`.`user_id`=`api_push_user`.`user_id` and `api_push_user_product`.`catalog_id`=`api_push_user`.`catalog_id` and `api_push_user_product`.`selection_id`=`api_push_user`.`selection_id`'}, #where
	    ##select_params=('user', 'catalog', 'selection',),# 'catalog', 'selection',
	    ##`selection_id`=%s
	    #)

	    #.annotate(books_count=Count('id'))
	    ordering = self.ordering or () # otherwise we might try to *None, which is bad ;)
	    if ordering:
		    qs = qs.order_by(*ordering)
	    return qs

	def push_fuction(self, obj):
	    return '<a href="%s" target="_blank">%s</a>' % ("/api/admin/api/push/"+str(obj.push.id), obj.push.id)
	push_fuction.allow_tags = True
	push_fuction.short_description = 'Push'
	push_fuction.admin_order_field = 'push'

	# ~ def pushed_products(self, obj):
	    # ~ try:
		# ~ return PushSellerPrice.objects.filter(selling_company=obj.selling_company, push=obj.push).count()
	    # ~ except:
		# ~ return ""

	# ~ def viewed_products(self, obj):
	    # ~ try:
		# ~ return CompanyProductFlat.objects.filter(buying_company=obj.buying_company, catalog=obj.catalog, selection=obj.selection, push_reference=obj.push, is_viewed="yes").count()
	    # ~ except:
		# ~ return ""

	'''def order_number(self, obj):
	    try:
		order_number = obj.sales_order.order_number
		return order_number
	    except:
		return ""
	order_number.admin_order_field = 'sales_order__order_number'''

admin.site.register(Push_User, Push_UserAdmin)

'''Push_User_ProductForm = select2_modelform(Push_User_Product, attrs={'width': '250px'})
class Push_User_ProductAdmin(admin.ModelAdmin):
	list_display = ('id', 'push_fuction', 'user', 'selling_company', 'buying_company', 'product', 'selection', 'catalog', 'is_viewed', 'price', 'selling_price', 'deleted',)
	list_filter = ('deleted', 'is_viewed', ('push__time', DateRangeFilter))
	search_fields = ('id', 'push__id', 'user__username', 'selling_company__name', 'buying_company__name', 'product__title', 'selection__name', 'catalog__title', 'is_viewed', 'price', 'selling_price', 'deleted',)
	#form = Push_User_ProductForm
	raw_id_fields = ('push', 'user', 'selection', 'catalog', 'selling_company', 'buying_company', 'product')

	def push_fuction(self, obj):
	    return '<a href="%s">%s</a>' % ("/api/admin/api/push/"+str(obj.push.id), obj.push.id)
	push_fuction.allow_tags = True
	push_fuction.short_description = 'Push'
	push_fuction.admin_order_field = 'push'

	def get_queryset(self, request):
		qs = self.model._default_manager.all_with_deleted().select_related('push', 'user', 'selling_company', 'buying_company', 'selection', 'catalog', 'product')
		ordering = self.ordering or () # otherwise we might try to *None, which is bad ;)
		if ordering:
			qs = qs.order_by(*ordering)
		return qs

admin.site.register(Push_User_Product, Push_User_ProductAdmin)'''

#admin.site.register(Push_Result)
###admin.site.register(Push_Catalog)
###admin.site.register(Push_Product)
###admin.site.register(Push_Selection)
###admin.site.register(Export)
###admin.site.register(Export_Result)
###admin.site.register(Export_Catalog)
###admin.site.register(Export_Product)

class InviteResource(resources.ModelResource):
	class Meta:
		model = Invite
		skip_unchanged = True
		report_skipped = False
		fields = ('id', 'relationship_type', 'user__username', 'company__name', 'time', )
		export_order = ('id', 'relationship_type', 'user__username', 'company__name', 'time', )

InviteForm = select2_modelform(Invite, attrs={'width': '250px'})
class InviteAdmin(ExportMixin, admin.ModelAdmin):
	list_display = ('id', 'relationship_type', 'user', 'company', 'time', )
	list_filter = ('relationship_type', ('time', DateRangeFilter))
	search_fields = ('id', 'relationship_type', 'user__username', 'company__name')
	resource_class = InviteResource
	#form = InviteForm
	raw_id_fields = ('company', 'user')

	def get_queryset(self, request):
	    return super(InviteAdmin, self).get_queryset(request).select_related('user', 'company')

admin.site.register(Invite, InviteAdmin)

class InviteeResource(resources.ModelResource):
	approve_status = fields.Field()
	buyer_group_type = fields.Field()
	invite_time_format = fields.Field()

	class Meta:
		model = Invitee
		skip_unchanged = True
		report_skipped = False
		fields = ('id', 'invite__user__username', 'invite__company__name', 'country__phone_code', 'invitee_number', 'invitee_company', 'invitee_name', 'status', 'registered_user__username', 'invite_type', 'invite_time_format', 'approve_status', 'buyer_group_type', 'invitation_type',)
		export_order = ('id', 'invite__user__username', 'invite__company__name', 'country__phone_code', 'invitee_number', 'invitee_company', 'invitee_name', 'status', 'registered_user__username', 'invite_type', 'invite_time_format', 'approve_status', 'buyer_group_type', 'invitation_type',)

	def get_queryset(self, request):
	    return super(InviteeResource, self).get_queryset(request).select_related('invite__user', 'invite__company', 'registered_user', 'country')

	def dehydrate_approve_status(self, invitee):
		try:
			global buyerObj
			buyerObj = Buyer.objects.filter(invitee=invitee.id).select_related('group_type').first()
			return buyerObj.status
		except:
			return ''

	def dehydrate_buyer_group_type(self, invitee):
		try:
			global buyerObj
			#buyerObj = Buyer.objects.filter(invitee=invitee.id).first()
			return buyerObj.group_type.name
		except:
			return ''

	def dehydrate_invite_time_format(self, invitee):
		try:
			return timezone.localtime(invitee.invite.time).strftime("%B %d, %Y, %I:%M%p") #.strftime("%Y-%m-%d %H:%M:%S")
		except:
			return ''

InviteeForm = select2_modelform(Invitee, attrs={'width': '250px'})
class InviteeAdmin(ExportMixin, admin.ModelAdmin):
	list_display = ('id', 'user', 'company', 'country', 'invitee_number', 'invitee_company', 'invitee_name', 'status', 'registered_user', 'invite_type', 'time', 'approve_status', 'buyer_group_type', 'invitation_type')
	list_filter = ('status', 'invite_type', 'invitation_type', ('invite__date', DateRangeFilter))
	search_fields = ('id', 'invite__user__username', 'invite__company__name', 'invitee_number', 'invitee_company', 'invitee_name', 'registered_user__username')
	resource_class = InviteeResource
	raw_id_fields = ('invite', 'country', 'registered_user')
	#form = InviteeForm

	def get_queryset(self, request):
	    return super(InviteeAdmin, self).get_queryset(request).select_related('invite__user', 'invite__company', 'registered_user', 'country').prefetch_related('invitee_id__group_type')

	def user(self, obj):
	    try:
		user = obj.invite.user.username
		return user
	    except:
		return ""
	user.admin_order_field = 'invite__user__username'

	def company(self, obj):
	    try:
		company = obj.invite.company.name
		return company
	    except:
		return ""
	company.admin_order_field = 'invite__company__name'



	def time(self, obj):
	    try:
		time = obj.invite.time
		return time
	    except:
		return ""
	time.admin_order_field = 'invite__time'

	def approve_status(self, obj):
	    try:
		global buyerObj
		# ~ buyerObj = Buyer.objects.filter(invitee=obj.id).select_related('group_type').first()
		# ~ return buyerObj.status
		buyerObj = obj.invitee_id.all()[0]
		return buyerObj.status
	    except:
		return ""

	def buyer_group_type(self, obj):
	    try:
		global buyerObj
		#buyerObj = Buyer.objects.filter(invitee=obj.id).first()
		return buyerObj.group_type.name
	    except:
		return ""

admin.site.register(Invitee, InviteeAdmin)

###admin.site.register(Message)
###admin.site.register(MessageFolder)

class MeetingResource(resources.ModelResource):
	person_name = fields.Field()
	company = fields.Field()
	#location = fields.Field()

	class Meta:
		model = Meeting
		skip_unchanged = True
		report_skipped = False
		fields = ('id', 'user', 'person_name', 'company', 'location_address', 'location_city', 'location_state', 'buying_company_ref__name', 'start_datetime', 'end_datetime', 'duration', 'status', 'note', 'purpose', 'buyer_name_text')
		export_order = ('id', 'user', 'person_name', 'company', 'location_address', 'location_city', 'location_state', 'buying_company_ref__name', 'start_datetime', 'end_datetime', 'duration', 'status', 'note', 'purpose', 'buyer_name_text')

	def get_queryset(self, request):
	    return super(MeetingResource, self).get_queryset(request).select_related('user__companyuser__company', 'buying_company_ref', 'company').order_by('-id')

	def dehydrate_person_name(self, obj):
	    try:
		global userObj
		userObj = obj.user
		fullname = userObj.first_name + " " + userObj.last_name
		return fullname
	    except:
		return ""

	def dehydrate_company(self, obj):
	    try:
		global userObj
		global companyObj
		companyObj = userObj.companyuser.company
		return companyObj.name
	    except:
		return ""

	#~ def dehydrate_location(self, obj):
	    #~ try:
		#~ geocodeObj = geocode(obj.start_lat, obj.start_long)

		#~ if geocodeObj['status'] == "OK":
		    #~ return geocodeObj['results'][0]['formatted_address']
	    #~ except:
	    	#~ return ""


MeetingForm = select2_modelform(Meeting, attrs={'width': '250px'})
class MeetingAdmin(ExportMixin, admin.ModelAdmin):
	list_display = ('id', 'user', 'person_name', 'company', 'location_address', 'location_city', 'location_state', 'buying_company_ref', 'start_datetime', 'end_datetime', 'duration', 'status', 'note', )
	list_filter = ('status', ('start_datetime', DateRangeFilter), ('end_datetime', DateRangeFilter) )
	search_fields = ('id', 'user__username', 'user__first_name', 'user__last_name', 'user__companyuser__company__name', 'location_address', 'location_city', 'location_state', 'buying_company_ref__name', 'note', )
	filter_horizontal = ('salesorder', )
	resource_class = MeetingResource
	raw_id_fields = ('salesorder', 'company', 'user', 'buying_company_ref')
	readonly_fields = ('created', 'modified',)
	#form = MeetingForm


	def get_queryset(self, request):
	    return super(MeetingAdmin, self).get_queryset(request).select_related('user__companyuser__company', 'buying_company_ref', 'company').order_by('-id')

	def person_name(self, obj):
	    try:
		global userObj
		userObj = obj.user
		fullname = userObj.first_name + " " + userObj.last_name
		return fullname
	    except:
		return ""
	person_name.admin_order_field = 'first_name'

	def company(self, obj):
	    try:
		global userObj
		global companyObj
		companyObj = userObj.companyuser.company
		return companyObj.name
	    except:
		return ""
	company.admin_order_field = 'companyuser__company__name'

	def location(self, obj):
	    try:
		#~ geocodeObj = geocode(obj.start_lat, obj.start_long)

		#~ if geocodeObj['status'] == "OK":
		    #~ return geocodeObj['results'][0]['formatted_address']
		return ""
	    except:
	    	return ""


admin.site.register(Meeting, MeetingAdmin)

BuyerSegmentationForm = select2_modelform(BuyerSegmentation, attrs={'width': '250px'})
class BuyerSegmentationAdmin(admin.ModelAdmin):
	list_display = ('id', 'segmentation_name', 'company', 'applozic_id', )
	#list_filter = ('id', 'company', )
	search_fields = ('id', 'segmentation_name', 'company__name', 'applozic_id', )
	filter_horizontal = ('state', 'city', 'category', 'buyers',)
	raw_id_fields = ('company',)
	form = BuyerSegmentationForm

	def get_queryset(self, request):
	    return super(BuyerSegmentationAdmin, self).get_queryset(request).select_related('company')

admin.site.register(BuyerSegmentation, BuyerSegmentationAdmin)

'''class StateAdmin(ImportExportModelAdmin, admin.ModelAdmin):
	list_display = ('id', 'state_name', )
	#list_filter = ('id', 'company', )
	search_fields = ('id', 'state_name', )

	resource_class = StateResource'''

class StateAdmin(admin.ModelAdmin):
	list_display = ('id', 'state_name', )
	search_fields = ('id', 'state_name', )

admin.site.register(State, StateAdmin)

class CityResource(resources.ModelResource):
    class Meta:
	    model = City
	    skip_unchanged = True
	    report_skipped = True
	    skip_row = True
	    fields = ('id', 'state', 'city_name', )
	    #exclude = ('id', )
	    import_id_fields = ('id', )
    def skip_row(self, instance, original):
        allfields = list(self.get_fields())

	#for field in allfields:
	#    print field.get_value(instance)

	allfields0 = allfields[0].get_value(instance)
	allfields1 = allfields[1].get_value(instance)
	allfields2 = allfields[2].get_value(instance)

	if City.objects.filter(state=allfields1, city_name=allfields2).exists():
	    return True

        if not self._meta.skip_unchanged:
            return False
        for field in self.get_fields():
            try:
                # For fields that are models.fields.related.ManyRelatedManager
                # we need to compare the results
                if list(field.get_value(instance).all()) != list(field.get_value(original).all()):
                    return False
            except AttributeError:
                if field.get_value(instance) != field.get_value(original):
                    return False
        return True

    '''without pk import
    def before_import(self, dataset, dry_run, **kwargs):
        dataset.insert_col(0, col=["",]*dataset.height, header="id")

    def get_instance(self, instance_loader, row):
        return False'''

CityForm = select2_modelform(City, attrs={'width': '250px'})
class CityAdmin(ImportExportModelAdmin, admin.ModelAdmin):
	list_display = ('id', 'city_name', 'state', )
	#list_filter = ('id', 'company', )
	search_fields = ('id', 'city_name', 'state__state_name', )
	form = CityForm
	resource_class = CityResource

	def get_queryset(self, request):
	    return super(CityAdmin, self).get_queryset(request).select_related('state')

	'''def save_model(self, request, obj, form, change):
	    print "CityAdmin save_model"
	    updateSegment = allSegmentationUpdate()
	    #print updateSegment
	    obj.save()'''

admin.site.register(City, CityAdmin)
#admin.site.register(MainCategory)
#admin.site.register(SubCategory)

CategoryForm = select2_modelform(Category, attrs={'width': '250px'})
class CategoryAdmin(admin.ModelAdmin):
	list_display = ('id', 'category_name', 'sort_order', 'created', 'modified',)
	#list_filter = ('id', 'company', )
	search_fields = ('id', 'category_name', 'sort_order',)
	form = CategoryForm
	readonly_fields = ('created', 'modified',)
admin.site.register(Category, CategoryAdmin)
#admin.site.register(Category)

'''InvoiceForm = select2_modelform(Invoice, attrs={'width': '250px'})
class InvoiceAdmin(admin.ModelAdmin):
	list_display = ('id', 'company', 'charges_amount', 'credit_amount', 'net_value', 'payment_status', 'payment_datetime', 'start_date', 'end_date')
	list_filter = ('payment_status', )
	search_fields = ('id', 'company__name', 'charges_amount', 'credit_amount', 'net_value', 'payment_status', 'payment_datetime', 'start_date', 'end_date')
	filter_horizontal = ('push', )
	form = InvoiceForm

	def get_queryset(self, request):
	    return super(InvoiceAdmin, self).get_queryset(request).select_related('company')

admin.site.register(Invoice, InvoiceAdmin)

InvoiceCreditForm = select2_modelform(InvoiceCredit, attrs={'width': '250px'})
class InvoiceCreditAdmin(admin.ModelAdmin):
	list_display = ('id', 'company', 'credit_amount', 'created_date', 'expire_date', )
	#list_filter = ('payment_status', )
	search_fields = ('id', 'company__name', 'credit_amount', 'created_date', 'expire_date', )
	form = InvoiceCreditForm

	def get_queryset(self, request):
	    return super(InvoiceCreditAdmin, self).get_queryset(request).select_related('company')

admin.site.register(InvoiceCredit, InvoiceCreditAdmin)'''

WishbookInvoiceForm = select2_modelform(WishbookInvoice, attrs={'width': '250px'})
class WishbookInvoiceAdmin(admin.ModelAdmin):
	list_display = ('id', 'company', 'billed_amount', 'start_date', 'end_date', )
	#list_filter = ('payment_status', )
	search_fields = ('id', 'company__name', 'billed_amount', 'start_date', 'end_date', )
	form = WishbookInvoiceForm
	raw_id_fields = ('company',)

	def get_queryset(self, request):
	    return super(WishbookInvoiceAdmin, self).get_queryset(request).select_related('company')

admin.site.register(WishbookInvoice, WishbookInvoiceAdmin)

WishbookInvoiceItemForm = select2_modelform(WishbookInvoiceItem, attrs={'width': '250px'})
class WishbookInvoiceItemAdmin(admin.ModelAdmin):
	list_display = ('id', 'company', 'item_type', 'amount', 'start_date', 'end_date', )
	#list_filter = ('payment_status', )
	search_fields = ('id', 'company__name', 'item_type', 'amount', 'start_date', 'end_date', )
	form = WishbookInvoiceItemForm
	raw_id_fields = ('invoice', 'company')

	def get_queryset(self, request):
	    return super(WishbookInvoiceItemAdmin, self).get_queryset(request).select_related('company')

admin.site.register(WishbookInvoiceItem, WishbookInvoiceItemAdmin)

WishbookCreditForm = select2_modelform(WishbookCredit, attrs={'width': '250px'})
class WishbookCreditAdmin(admin.ModelAdmin):
	list_display = ('id', 'company', 'amount', 'balance_amount', 'expire_date', )
	#list_filter = ('payment_status', )
	search_fields = ('id', 'company__name', 'amount', 'balance_amount', 'expire_date', )
	form = WishbookCreditForm
	raw_id_fields = ('company', )

	def get_queryset(self, request):
	    return super(WishbookCreditAdmin, self).get_queryset(request).select_related('company')

admin.site.register(WishbookCredit, WishbookCreditAdmin)

WishbookInvoiceCreditForm = select2_modelform(WishbookInvoiceCredit, attrs={'width': '250px'})
class WishbookInvoiceCreditAdmin(admin.ModelAdmin):
	list_display = ('id', 'company', 'credit', 'amount',)
	#list_filter = ('payment_status', )
	search_fields = ('id', 'invoice', 'credit', 'amount',)
	form = WishbookInvoiceCreditForm
	raw_id_fields = ('invoice', 'credit')

	def get_queryset(self, request):
	    return super(WishbookInvoiceCreditAdmin, self).get_queryset(request).select_related('invoice__company')

	def company(self, obj):
	    try:
		company = obj.invoice.company.name #Or change this to how you would access the userprofile object - This was assuming that the User, Profile relationship is OneToOne
		return company
	    except:
		return ""
	#company.admin_order_field = 'invoice__company__name'

admin.site.register(WishbookInvoiceCredit, WishbookInvoiceCreditAdmin)

admin.site.register(WishbookPayment)
admin.site.register(WishbookInvoicePayment)

class RegistrationOTPAdmin(admin.ModelAdmin):
	list_display = ('id', 'phone_number', 'otp', 'created_date', 'is_verified', )
	list_filter = ('is_verified', ('created_date', DateRangeFilter))
	search_fields = ('id', 'phone_number', 'otp')

admin.site.register(RegistrationOTP, RegistrationOTPAdmin)

CompanyPhoneAliasForm = select2_modelform(CompanyPhoneAlias, attrs={'width': '250px'})
class CompanyPhoneAliasAdmin(admin.ModelAdmin):
	list_display = ('id', 'company', 'country', 'alias_number', 'status', 'created', 'modified',)
	list_filter = ('status', )
	search_fields = ('id', 'company__name', 'country__name', 'alias_number',)
	form = CompanyPhoneAliasForm
	raw_id_fields = ('company', )
	readonly_fields = ('created', 'modified',)

	def get_queryset(self, request):
	    return super(CompanyPhoneAliasAdmin, self).get_queryset(request).select_related('company', 'country')

admin.site.register(CompanyPhoneAlias, CompanyPhoneAliasAdmin)

class UnregisteredPhoneAliasResource(resources.ModelResource):
    class Meta:
	    model = UnregisteredPhoneAlias
	    skip_unchanged = True
	    report_skipped = True
	    skip_row = True
	    fields = ('id', 'master_country', 'master_number', 'alias_country', 'alias_number', )
	    #exclude = ('id', )
	    import_id_fields = ('id', )
    def skip_row(self, instance, original):
        allfields = list(self.get_fields())

	#for field in allfields:
	#    print field.get_value(instance)

	allfields0 = allfields[0].get_value(instance)
	allfields1 = allfields[1].get_value(instance)
	allfields2 = allfields[2].get_value(instance)
	allfields3 = allfields[3].get_value(instance)
	allfields4 = allfields[4].get_value(instance)

	if UnregisteredPhoneAlias.objects.filter(master_country=allfields1, master_number=allfields2, alias_country=allfields3, alias_number=allfields4).exists():
	    return True

        if not self._meta.skip_unchanged:
            return False
        for field in self.get_fields():
            try:
                # For fields that are models.fields.related.ManyRelatedManager
                # we need to compare the results
                if list(field.get_value(instance).all()) != list(field.get_value(original).all()):
                    return False
            except AttributeError:
                if field.get_value(instance) != field.get_value(original):
                    return False
        return True

class UnregisteredPhoneAliasAdmin(ImportExportModelAdmin, admin.ModelAdmin):
	list_display = ('id', 'master_country', 'master_number', 'alias_country', 'alias_number', 'created', 'modified',)
	list_filter = ('master_country', 'alias_country',)
	search_fields = ('id', 'master_country__name', 'master_number', 'alias_country__name', 'alias_number',)
	resource_class = UnregisteredPhoneAliasResource
	readonly_fields = ('created', 'modified',)

	def get_queryset(self, request):
	    return super(UnregisteredPhoneAliasAdmin, self).get_queryset(request).select_related('master_country', 'alias_country')

admin.site.register(UnregisteredPhoneAlias, UnregisteredPhoneAliasAdmin)

class CountryAdmin(admin.ModelAdmin):
	list_display = ('id', 'name', 'phone_code',)
	search_fields = ('id', 'name', 'phone_code',)

admin.site.register(Country, CountryAdmin)

class CompanyNumberAdmin(admin.ModelAdmin):
	list_display = ('id', 'phone_number', 'alias_number', 'is_verified', 'created', 'modified', )
	list_filter = ('is_verified', )
	search_fields = ('id', 'phone_number', 'alias_number', 'is_verified', )
	readonly_fields = ('created', 'modified',)

admin.site.register(CompanyNumber, CompanyNumberAdmin)

CompanyPriceListForm = select2_modelform(CompanyPriceList, attrs={'width': '250px'})
class CompanyPriceListAdmin(admin.ModelAdmin):
	list_display = ('id', 'company', 'number_pricelists', 'pricelist2_multiplier')
	search_fields = ('id', 'company__name', 'number_pricelists', 'pricelist2_multiplier')
	form = CompanyPriceListForm
	raw_id_fields = ('company',)

	def get_queryset(self, request):
	    return super(CompanyPriceListAdmin, self).get_queryset(request).select_related('company')

admin.site.register(CompanyPriceList, CompanyPriceListAdmin)

CompanyBuyerGroupForm = select2_modelform(CompanyBuyerGroup, attrs={'width': '250px'})
class CompanyBuyerGroupAdmin(admin.ModelAdmin):
	list_display = ('id', 'company_detail', 'buyer_type', 'payment_duration', 'discount', 'cash_discount', 'created', 'modified',)
	search_fields = ('id', 'company__name', 'buyer_type', 'payment_duration', 'discount', 'cash_discount')
	list_filter = ('buyer_type',)
	#form = CompanyBuyerGroupForm
	raw_id_fields = ('company', )
	readonly_fields = ('created', 'modified',)

	def get_queryset(self, request):
	    return super(CompanyBuyerGroupAdmin, self).get_queryset(request).select_related('company')

	def company_detail(self, obj):
		if obj.company:
			return '<a href="%s" target="_blank">%s</a>' % ("/api/admin/api/company/"+str(obj.company.id), obj.company)
		return None
	company_detail.allow_tags = True
	company_detail.short_description = 'Company'
	company_detail.admin_order_field = 'company_id'

admin.site.register(CompanyBuyerGroup, CompanyBuyerGroupAdmin)

class GroupTypeAdmin(admin.ModelAdmin):
	list_display = ('id', 'name', )
	#list_filter = ('payment_status', )
	search_fields = ('id', 'name', )

admin.site.register(GroupType, GroupTypeAdmin)

class CategoryEavAttributeAdmin(admin.ModelAdmin):
	list_display = ('id', 'category', 'attribute', 'created', 'modified', )
	#list_filter = ('payment_status', )
	search_fields = ('id', 'category__category_name', 'attribute__name', )
	#filter_horizontal = ('attribute', )
	readonly_fields = ('created', 'modified',)

	'''def attributes(self, obj):
	    try:
		name = obj.attribute.all().values_list('name', flat=True).distinct()
		return ', '.join(name)
	    except:
		return ""'''

admin.site.register(CategoryEavAttribute, CategoryEavAttributeAdmin)

#admin.site.register(ImageTest, SoftDeleteAdmin)#SimpleHistoryAdmin

class CompanyTypeResource(resources.ModelResource):
	company_types = fields.Field()

	class Meta:
		model = CompanyType
		skip_unchanged = True
		report_skipped = False
		fields = ('id', 'company__name', 'company_types', 'manufacturer', 'wholesaler_distributor', 'retailer', 'online_retailer_reseller', 'broker',)
		export_order = ('id', 'company__name', 'company_types', 'manufacturer', 'wholesaler_distributor', 'retailer', 'online_retailer_reseller', 'broker',)

	def dehydrate_company_types(self, obj):
		try:
			arr = []
			if obj.manufacturer is True:
			    arr.append('Manufacturer')
			if obj.wholesaler_distributor is True:
			    arr.append('Wholesaler Distributor')
			if obj.retailer is True:
			    arr.append('Retailer')
			if obj.online_retailer_reseller is True:
			    arr.append('Online Retailer Reseller')
			if obj.broker is True:
			    arr.append('Broker')

			return arr
		except:
			return ''

CompanyTypeForm = select2_modelform(CompanyType, attrs={'width': '250px'})
class CompanyTypeAdmin(ExportMixin, admin.ModelAdmin):
	list_display = ('id', 'company_detail', 'company_types', 'manufacturer', 'wholesaler_distributor', 'retailer', 'online_retailer_reseller', 'broker', 'created', 'modified',)
	search_fields = ('id', 'company__name', 'company__phone_number', 'manufacturer', 'wholesaler_distributor', 'retailer', 'online_retailer_reseller', 'broker')
	form = CompanyTypeForm
	resource_class = CompanyTypeResource
	raw_id_fields = ('company', )
	readonly_fields = ('created', 'modified',)

	def get_queryset(self, request):
	    return super(CompanyTypeAdmin, self).get_queryset(request).select_related('company')

	def company_types(self, obj):
	    try:
		arr = []
		if obj.manufacturer is True:
		    arr.append('Manufacturer')
		if obj.wholesaler_distributor is True:
		    arr.append('Wholesaler Distributor')
		if obj.retailer is True:
		    arr.append('Retailer')
		if obj.online_retailer_reseller is True:
		    arr.append('Online Retailer Reseller')
		if obj.broker is True:
		    arr.append('Broker')

		return arr
	    except:
		return ""

	def company_detail(self, obj):
		if obj.company:
			return '<a href="%s" target="_blank">%s</a>' % ("/api/admin/api/company/"+str(obj.company.id), obj.company)
		return None
	company_detail.allow_tags = True
	company_detail.short_description = 'Company'
	company_detail.admin_order_field = 'company_id'

admin.site.register(CompanyType, CompanyTypeAdmin)

class PromotionalNotificationAdmin(admin.ModelAdmin):
	list_display = ('id', 'title', 'text', 'app_version', 'last_login_platform')
	search_fields = ('id', 'title', 'text', 'app_version', 'last_login_platform')
	list_filter = ('last_login_platform', )
	filter_horizontal = ('state', 'city', )
	raw_id_fields = ('user', )

	def save_model(self, request, obj, form, change):
	    obj.save()

	    #category = form.cleaned_data['category']
	    state = form.cleaned_data['state']
	    city = form.cleaned_data['city']
	    user = form.cleaned_data['user']
	    title = form.cleaned_data['title']
	    text = form.cleaned_data['text']
	    #image = obj.image.thumbnail[settings.MEDIUM_IMAGE].url

	    manufacturer = form.cleaned_data['manufacturer']
	    wholesaler_distributor = form.cleaned_data['wholesaler_distributor']
	    retailer = form.cleaned_data['retailer']
	    online_retailer_reseller = form.cleaned_data['online_retailer_reseller']
	    broker = form.cleaned_data['broker']
	    company_type_not_selected = form.cleaned_data['company_type_not_selected']

	    app_version = form.cleaned_data['app_version']
	    last_login_platform = form.cleaned_data['last_login_platform']
	    deep_link = form.cleaned_data['deep_link']


	    companies = []

	    if len(state) > 0 or len(city) > 0:
		cids = Company.objects.filter(state__in = state, city__in = city).values_list('id', flat=True)
		companies.extend(list(cids))
	    else:
		cids = Company.objects.all().values_list('id', flat=True)
		companies.extend(list(cids))


	    companies_type = []
	    is_companies_type_filter = False
	    if manufacturer:
		ct=CompanyType.objects.filter(company__in=companies, manufacturer=True).values_list('company', flat=True).distinct()
		companies_type.extend(list(ct))
		is_companies_type_filter = True
	    if wholesaler_distributor:
		ct=CompanyType.objects.filter(company__in=companies, wholesaler_distributor=True).values_list('company', flat=True).distinct()
		companies_type.extend(list(ct))
		is_companies_type_filter = True
	    if retailer:
		ct=CompanyType.objects.filter(company__in=companies, retailer=True).values_list('company', flat=True).distinct()
		companies_type.extend(list(ct))
		is_companies_type_filter = True
	    if online_retailer_reseller:
		ct=CompanyType.objects.filter(company__in=companies, online_retailer_reseller=True).values_list('company', flat=True).distinct()
		companies_type.extend(list(ct))
		is_companies_type_filter = True
	    if broker:
		ct=CompanyType.objects.filter(company__in=companies, broker=True).values_list('company', flat=True).distinct()
		companies_type.extend(list(ct))
		is_companies_type_filter = True
	    if company_type_not_selected:
		ct=CompanyType.objects.filter(company__in=companies, manufacturer=False, wholesaler_distributor=False, retailer=False, online_retailer_reseller=False, broker=False).values_list('company', flat=True).distinct()
		companies_type.extend(list(ct))
		is_companies_type_filter = True

	    if is_companies_type_filter:
		companies = companies_type


	    print "companies=",companies


	    userids = CompanyUser.objects.filter(company__in=companies).values_list('user', flat=True)

	    if app_version:
		userids = UserPlatformInfo.objects.filter(user__in=userids, app_version=app_version).values_list('user', flat=True)

	    if last_login_platform:
		userids = UserProfile.objects.filter(user__in=userids, last_login_platform=last_login_platform).values_list('user', flat=True)

	    #userids = User.objects.filter(Q(id__in=userids)|Q(id__in=user)).values_list('id', flat=True).distinct()

	    # ~ if is_companies_type_filter==False and len(state) <= 0 and len(city) <= 0:
		# ~ userids = User.objects.filter(id__in=user).values_list('id', flat=True).distinct()
	    # ~ else:
		# ~ userids = User.objects.filter(Q(id__in=userids)|Q(id__in=user)).values_list('id', flat=True).distinct()
	    if len(user) > 0:
		userids = User.objects.filter(id__in=user).values_list('id', flat=True).distinct()

	    userids = list(userids)
	    print "userids=",userids


	    rno = random.randrange(100000, 999999, 1)
	    notification_image = ""
	    if obj.image:
		notification_image = obj.image.url


	    not_json = {"notId": rno, "title":title, "push_type":"promotional", "image":notification_image}
	    if deep_link:
		not_json["other_para"] = {"deep_link":str(deep_link)}

	    if settings.TASK_QUEUE_METHOD == 'celery':
		notificationSend.apply_async((userids, text, not_json), expires=datetime.now() + timedelta(days=2))
	    elif settings.TASK_QUEUE_METHOD == 'djangoQ':
		task_id = async(
			'api.tasks.notificationSend',
			userids, text, not_json
		)

	    obj.save()

admin.site.register(PromotionalNotification, PromotionalNotificationAdmin)


class UpdateNotificationAdmin(admin.ModelAdmin):
	list_display = ('id', 'title', 'text', 'update_for', 'app_version_code')
	search_fields = ('id', 'title', 'text', 'update_for', 'app_version_code')
	list_filter = ('update_for', )

	def save_model(self, request, obj, form, change):
	    obj.save()

	    title = form.cleaned_data['title']
	    text = form.cleaned_data['text']
	    app_version_code = form.cleaned_data['app_version_code']

	    rno = random.randrange(100000, 999999, 1)
	    image = settings.MEDIA_URL+"logo-single.png"

	    #~ ids = User.objects.all().values_list('id', flat=True).distinct()
	    #~ ids = list(ids)

	    if obj.update_for == "Android":
		print "Android"
		excludeUsers = UserPlatformInfo.objects.filter(app_version_code__gt=app_version_code).values_list('user', flat=True)
		ids = UserProfile.objects.filter(last_login_platform="Android").exclude(user__in=excludeUsers).values_list('user', flat=True)
		ids = list(ids)

		logger.info("UpdateNotificationAdmin Android users = %s"% (ids))

		if settings.TASK_QUEUE_METHOD == 'celery':
		    notificationSend.apply_async((ids, text, {"notId": rno, "title":title, "push_type":"update", "image":image}, 'gcm'), expires=datetime.now() + timedelta(days=2))
		elif settings.TASK_QUEUE_METHOD == 'djangoQ':
		    task_id = async(
			    'api.tasks.notificationSend',
			    ids, text, {"notId": rno, "title":title, "push_type":"update", "image":image}, 'gcm'
		    )

	    elif obj.update_for == "IOS":
		print "IOS"
		excludeUsers = UserPlatformInfo.objects.filter(app_version_code__gt=app_version_code).values_list('user', flat=True)
		ids = UserProfile.objects.filter(last_login_platform="iOS").exclude(user__in=excludeUsers).values_list('user', flat=True)
		ids = list(ids)

		logger.info("UpdateNotificationAdmin IOS users = %s"% (ids))

		if settings.TASK_QUEUE_METHOD == 'celery':
		    notificationSend.apply_async((ids, text, {"notId": rno, "title":title, "push_type":"update", "image":image}, 'apns'), expires=datetime.now() + timedelta(days=2))
		elif settings.TASK_QUEUE_METHOD == 'djangoQ':
		    task_id = async(
			    'api.tasks.notificationSend',
			    ids, text, {"notId": rno, "title":title, "push_type":"update", "image":image}, 'apns'
		    )

	    obj.save()

admin.site.register(UpdateNotification, UpdateNotificationAdmin)

WarehouseTypeForm = select2_modelform(Warehouse, attrs={'width': '250px'})
class WarehouseAdmin(admin.ModelAdmin):
	list_display = ('id', 'company', 'name',)
	search_fields = ('id', 'company__name', 'name',)
	form = WarehouseTypeForm
	raw_id_fields = ('company', 'supplier', 'salesmen',)

	def get_queryset(self, request):
	    return super(WarehouseAdmin, self).get_queryset(request).select_related('company')

admin.site.register(Warehouse, WarehouseAdmin)

StockForm = select2_modelform(Stock, attrs={'width': '250px'})
class StockAdmin(admin.ModelAdmin):
	list_display = ('id', 'warehouse', 'company', 'catalog', 'product', 'in_stock', 'available', 'blocked', 'open_sale', 'open_purchase',)
	search_fields = ('id', 'warehouse__name', 'company__name', 'product__catalog__title', 'product__title', 'in_stock', 'available', 'blocked', 'open_sale', 'open_purchase',)
	form = StockForm
	raw_id_fields = ('warehouse', 'product', 'company')
	list_editable = ("in_stock",)

	def get_queryset(self, request):
	    return super(StockAdmin, self).get_queryset(request).select_related('warehouse', 'product')

	def catalog(self, obj):
	    try:
		return obj.product.catalog.title
	    except:
		return ""
	catalog.admin_order_field = 'product__catalog__title'

admin.site.register(Stock, StockAdmin)

WarehouseStockForm = select2_modelform(WarehouseStock, attrs={'width': '250px'})
class WarehouseStockAdmin(admin.ModelAdmin):
	list_display = ('id', 'warehouse', 'product', 'in_stock', )
	search_fields = ('id', 'warehouse__name', 'product__title', 'in_stock', )
	form = WarehouseStockForm
	raw_id_fields = ('warehouse', 'product')

	def get_queryset(self, request):
	    return super(WarehouseStockAdmin, self).get_queryset(request).select_related('warehouse', 'product')

admin.site.register(WarehouseStock, WarehouseStockAdmin)

OpeningStockForm = select2_modelform(OpeningStock, attrs={'width': '250px'})
class OpeningStockAdmin(admin.ModelAdmin):
	list_display = ('id', 'warehouse', )
	search_fields = ('id', 'warehouse__name', )
	form = OpeningStockForm
	raw_id_fields = ('warehouse', 'user', 'company')

	def get_queryset(self, request):
	    return super(OpeningStockAdmin, self).get_queryset(request).select_related('warehouse')

admin.site.register(OpeningStock, OpeningStockAdmin)

OpeningStockQtyForm = select2_modelform(OpeningStockQty, attrs={'width': '250px'})
class OpeningStockQtyAdmin(admin.ModelAdmin):
	list_display = ('id', 'product', 'opening_stock', 'in_stock', )
	search_fields = ('id', 'product__title', 'opening_stock', 'in_stock', )
	form = OpeningStockQtyForm
	raw_id_fields = ('product', 'opening_stock')

	def get_queryset(self, request):
	    return super(OpeningStockQtyAdmin, self).get_queryset(request).select_related('product')

admin.site.register(OpeningStockQty, OpeningStockQtyAdmin)

InventoryAdjustmentForm = select2_modelform(InventoryAdjustment, attrs={'width': '250px'})
class InventoryAdjustmentAdmin(admin.ModelAdmin):
	list_display = ('id', 'warehouse', )
	search_fields = ('id', 'warehouse__name',  )
	form = InventoryAdjustmentForm
	raw_id_fields = ('warehouse', 'user', 'company')

	def get_queryset(self, request):
	    return super(InventoryAdjustmentAdmin, self).get_queryset(request).select_related('warehouse')

admin.site.register(InventoryAdjustment, InventoryAdjustmentAdmin)

InventoryAdjustmentQtyForm = select2_modelform(InventoryAdjustmentQty, attrs={'width': '250px'})
class InventoryAdjustmentQtyAdmin(admin.ModelAdmin):
	list_display = ('id', 'inventory_adjustment', 'product', 'quantity', 'adjustment_type', 'to_warehouse', )
	search_fields = ('id', 'inventory_adjustment', 'product__title', 'quantity', 'adjustment_type', 'to_warehouse', )
	form = InventoryAdjustmentQtyForm
	raw_id_fields = ('inventory_adjustment', 'product', 'to_warehouse')
	def get_queryset(self, request):
	    return super(InventoryAdjustmentQtyAdmin, self).get_queryset(request).select_related('inventory_adjustment','product')

admin.site.register(InventoryAdjustmentQty, InventoryAdjustmentQtyAdmin)


ProductStatusForm = select2_modelform(ProductStatus, attrs={'width': '250px'})
class ProductStatusAdmin(admin.ModelAdmin):
	list_display = ('id', 'company', 'product', 'status', 'created', 'modified',)
	list_filter = ('status',)
	search_fields = ('company__id', 'company__name', 'product__sku', 'product__id')
	#form = ProductStatusForm
	raw_id_fields = ('company', 'product', 'user')
	readonly_fields = ('created', 'modified',)
	def get_queryset(self, request):
	    return super(ProductStatusAdmin, self).get_queryset(request).select_related('company', 'product')

admin.site.register(ProductStatus, ProductStatusAdmin)

CatalogSelectionStatusForm = select2_modelform(CatalogSelectionStatus, attrs={'width': '250px'})
class CatalogSelectionStatusAdmin(admin.ModelAdmin):
	list_display = ('id', 'company', 'catalog_detail', 'selection', 'status', 'created', 'modified',)
	list_filter = ('status',)
	search_fields = ('id', 'company__name', 'catalog__title', 'selection__name')
	raw_id_fields = ('company', 'catalog', 'selection', 'user')
	readonly_fields = ('created', 'modified',)
	#form = CatalogSelectionStatusForm
	def get_queryset(self, request):
	    return super(CatalogSelectionStatusAdmin, self).get_queryset(request).select_related('company', 'catalog', 'selection')

	def catalog_detail(self, obj):
	    return '<a href="%s" target="_blank">%s</a>' % ("/api/admin/api/catalog/"+str(obj.catalog.id), obj.catalog)
	catalog_detail.allow_tags = True
	catalog_detail.short_description = 'Catalog Details'
	catalog_detail.admin_order_field = 'catalog__id'

admin.site.register(CatalogSelectionStatus, CatalogSelectionStatusAdmin)
#admin.site.register(CatalogSelectionStatus)

'''class DispatchAdmin(admin.ModelAdmin):
	list_display = ('id', 'date', 'dispatch_details', 'status',)
	search_fields = ('id', 'date', 'dispatch_details', 'status',)
	raw_id_fields = ('sales_order',)

admin.site.register(Dispatch, DispatchAdmin)

class DispatchItemAdmin(admin.ModelAdmin):
	list_display = ('id', 'sales_order_item', 'quantity', )
	search_fields = ('id', 'sales_order_item__product__title', 'quantity', )
	raw_id_fields = ('sales_order_item',)

	def get_queryset(self, request):
	    return super(DispatchItemAdmin, self).get_queryset(request).select_related('sales_order_item__product')

admin.site.register(DispatchItem, DispatchItemAdmin)'''

class AppAdmin(admin.ModelAdmin):
	list_display = ('id', 'name', 'api_min_version', 'api_max_version',)
	search_fields = ('id', 'name', 'api_min_version', 'api_max_version',)
	readonly_fields = ('created', 'modified',)

admin.site.register(App, AppAdmin)

AppInstanceForm = select2_modelform(AppInstance, attrs={'width': '250px'})
class AppInstanceAdmin(admin.ModelAdmin):
	list_display = ('id', 'app', 'company', )
	search_fields = ('id', 'app__name', 'company__name', )
	raw_id_fields = ('company',)
	form = AppInstanceForm
	readonly_fields = ('created', 'modified',)

admin.site.register(AppInstance, AppInstanceAdmin)

SKUMapForm = select2_modelform(SKUMap, attrs={'width': '250px'})
class SKUMapAdmin(admin.ModelAdmin):
	list_display = ('id', 'app_instance', 'product', 'external_sku', 'catalog', 'external_catalog', 'created', 'modified',)
	search_fields = ('id', 'app_instance__app__name', 'product__sku', 'external_sku', 'catalog__title', 'external_catalog')
	form = SKUMapForm
	raw_id_fields = ('product','catalog')
	readonly_fields = ('created', 'modified',)

admin.site.register(SKUMap, SKUMapAdmin)

BarcodeForm = select2_modelform(Barcode, attrs={'width': '250px'})
class BarcodeAdmin(admin.ModelAdmin):
	list_display = ('id', 'warehouse', 'product', 'barcode',)
	search_fields = ('id', 'warehouse__name', 'product__sku', 'barcode',)
	form = BarcodeForm
	raw_id_fields = ('warehouse', 'product', 'user')

admin.site.register(Barcode, BarcodeAdmin)

CompanyProductFlatForm = select2_modelform(CompanyProductFlat, attrs={'width': '250px'})
class CompanyProductFlatAdmin(admin.ModelAdmin):
	list_display = ('id', 'product', 'selling_company', 'buying_company', 'final_price', 'selling_price', 'catalog', 'is_viewed',)
	list_filter = ('is_viewed', 'is_disable', 'like',)
	search_fields = ('id', 'product__title', 'product__sku', 'selling_company__name', 'buying_company__name', 'final_price', 'selling_price', 'catalog__title', )
	raw_id_fields = ('product', 'buying_company', 'selection', 'catalog', 'selling_company', 'push_reference')
	#form = CompanyProductFlatForm

	def get_queryset(self, request):
	    return super(CompanyProductFlatAdmin, self).get_queryset(request).select_related('product', 'selling_company__name', 'buying_company__name', 'catalog__title')

admin.site.register(CompanyProductFlat, CompanyProductFlatAdmin)

class UnsubscribedNumberResource(resources.ModelResource):
    class Meta:
	    model = UnsubscribedNumber
	    skip_unchanged = True
	    report_skipped = True
	    skip_row = True
	    fields = ('id', 'country', 'phone_number', )
	    #exclude = ('id', )
	    import_id_fields = ('id', )
    def skip_row(self, instance, original):
        allfields = list(self.get_fields())

	#for field in allfields:
	#    print field.get_value(instance)

	allfields0 = allfields[0].get_value(instance)
	allfields1 = allfields[1].get_value(instance)
	allfields2 = allfields[2].get_value(instance)

	if UnsubscribedNumber.objects.filter(country=allfields1, phone_number=allfields2).exists():
	    return True

        if not self._meta.skip_unchanged:
            return False
        for field in self.get_fields():
            try:
                # For fields that are models.fields.related.ManyRelatedManager
                # we need to compare the results
                if list(field.get_value(instance).all()) != list(field.get_value(original).all()):
                    return False
            except AttributeError:
                if field.get_value(instance) != field.get_value(original):
                    return False
        return True

UnsubscribedNumberForm = select2_modelform(UnsubscribedNumber, attrs={'width': '250px'})
class UnsubscribedNumberAdmin(ImportExportModelAdmin, admin.ModelAdmin):
	list_display = ('id', 'country', 'phone_number', 'created', 'modified',)
	search_fields = ('id', 'country__name', 'phone_number', )
	form = UnsubscribedNumberForm
	resource_class = UnsubscribedNumberResource
	readonly_fields = ('created', 'modified',)

	def get_queryset(self, request):
	    return super(UnsubscribedNumberAdmin, self).get_queryset(request).select_related('country')

admin.site.register(UnsubscribedNumber, UnsubscribedNumberAdmin)

class SmsTransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at', 'total_sent', 'provider', )
    list_filter = (('created_at', DateRangeFilter), )
    search_fields = ('id', 'created_at', 'total_sent', 'provider', )
admin.site.register(SmsTransaction, SmsTransactionAdmin)

class ProductEAVFlatAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'category', 'catalog', 'fabric', 'work', 'fabric_text', 'work_text', )
    search_fields = ('id', 'product__title', 'category__category_name', 'catalog__title', 'fabric', 'work', 'fabric_text', 'work_text', )
    raw_id_fields = ('product', 'category', 'catalog')

    def get_queryset(self, request):
	    return super(ProductEAVFlatAdmin, self).get_queryset(request).select_related('product', 'category', 'catalog')

admin.site.register(ProductEAVFlat, ProductEAVFlatAdmin)

class AttendanceResource(resources.ModelResource):
	person_name = fields.Field()
	#company = fields.Field()
	#location = fields.Field()

	class Meta:
		model = Attendance
		skip_unchanged = True
		report_skipped = False
		fields = ('id', 'user', 'person_name', 'company__name', 'date_time', 'action', 'att_lat', 'att_long',)
		export_order = ('id', 'user', 'person_name', 'company__name', 'date_time', 'action', 'att_lat', 'att_long',)

	def dehydrate_person_name(self, obj):
	    try:
		global userObj
		userObj = obj.user
		fullname = userObj.first_name + " " + userObj.last_name
		return fullname
	    except:
		return ""

	#~ def dehydrate_company(self, obj):
	    #~ try:
		#~ global userObj
		#~ global companyObj
		#~ companyObj = userObj.companyuser.company
		#~ return companyObj.name
	    #~ except:
		#~ return ""

	#~ def dehydrate_location(self, obj):
	    #~ try:
		#~ geocodeObj = geocode(obj.att_lat, obj.att_long)

		#~ if geocodeObj['status'] == "OK":
		    #~ return geocodeObj['results'][0]['formatted_address']
	    #~ except:
		#~ return ""

class AttendanceAdmin(ExportMixin, admin.ModelAdmin):
    list_display = ('id', 'user', 'person_name', 'company', 'date_time', 'action', 'att_lat', 'att_long', 'created', 'modified',)
    search_fields = ('id', 'date_time', 'action', 'att_lat', 'att_long', 'user__username', 'user__first_name', 'user__last_name', 'user__companyuser__company__name', )
    resource_class = AttendanceResource
    raw_id_fields = ('company', 'user')
    readonly_fields = ('created', 'modified',)

    def person_name(self, obj):
	try:
	    global userObj
	    userObj = obj.user
	    fullname = userObj.first_name + " " + userObj.last_name
	    return fullname
	except:
	    return ""
    person_name.admin_order_field = 'user__first_name'

    #~ def company(self, obj):
	#~ try:
	    #~ global userObj
	    #~ global companyObj
	    #~ companyObj = userObj.companyuser.company
	    #~ return companyObj.name
	#~ except:
	    #~ return ""
    #~ company.admin_order_field = 'user__companyuser__company__name'

    #~ def location(self, obj):
	#~ try:
	    #~ geocodeObj = geocode(obj.att_lat, obj.att_long)

	    #~ if geocodeObj['status'] == "OK":
		#~ return geocodeObj['results'][0]['formatted_address']
	#~ except:
	    #~ return ""

admin.site.register(Attendance, AttendanceAdmin)


class LogisticsAdmin(admin.ModelAdmin):
	list_display = ('id', 'name',)
	search_fields = ('id', 'name',)

admin.site.register(Logistics, LogisticsAdmin)

class CronHistoryAdmin(admin.ModelAdmin):
	list_display = ('id', 'cron_type', 'time')
	search_fields = ('id', 'cron_type', 'time')

admin.site.register(CronHistory, CronHistoryAdmin)

class SmsErrorAdmin(admin.ModelAdmin):
	list_display = ('id', 'created_at', 'mobile_no', 'is_sent', 'provider')
	search_fields = ('id', 'created_at', 'mobile_no', 'is_sent', 'provider')
	list_filter = ('is_sent', ('created_at', DateRangeFilter),)
	actions = ['send_sms']

	def send_sms(self, request, queryset):
	    #ids = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
	    ids = queryset.values_list('id', flat=True).distinct()
	    ids = list(ids)

	    smserrorObjs = SmsError.objects.filter(id__in=ids, is_sent=False).order_by('created_at')

	    for smserrorObj in smserrorObjs:
		    print smserrorObj.id
		    smsSend([smserrorObj.mobile_no], smserrorObj.sms_text, True)
		    smserrorObj.is_sent = True
		    smserrorObj.save()

	    messages.success(request, 'Send error sms')
	    return
	send_sms.short_description = u'Send SMS'

admin.site.register(SmsError, SmsErrorAdmin)

class CompanyAccountResource(resources.ModelResource):
    class Meta:
	model = CompanyAccount
	skip_unchanged = True
	report_skipped = False
	fields = ('id', 'company__name', 'buyer_company__name', 'mapped_accout_ref', )
	export_order = ('id', 'company__name', 'buyer_company__name', 'mapped_accout_ref', )


class CompanyAccountAdmin(ExportMixin, admin.ModelAdmin):
	list_display = ('id', 'company', 'buyer_company', 'mapped_accout_ref')
	search_fields = ('id', 'company', 'buyer_company', 'mapped_accout_ref')
	resource_class = CompanyAccountResource
	raw_id_fields = ('company', 'buyer_company')
	readonly_fields = ('created', 'modified',)

admin.site.register(CompanyAccount, CompanyAccountAdmin)

'''
class CompanyAccountAdmin(admin.ModelAdmin):
	list_display = ('id', 'buyer_company','mapped_accout_ref',)
	search_fields = ('id', 'buyer_company__name','mapped_accout_ref',)

admin.site.register(CompanyAccount, CompanyAccountAdmin)
'''

class PaymentInline(admin.TabularInline):
    model = Payment.invoice.through
    extra = 0
    show_change_link = True
    #raw_id_fields = ('id',)

class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 1
    show_change_link = True
    raw_id_fields = ('order_item',)

class InvoiceResource(resources.ModelResource):
	created_date = fields.Field()

	class Meta:
		model = Invoice
		skip_unchanged = True
		report_skipped = False
		fields = ('id', 'invoice_number', 'order__id', 'order__order_number', 'created_date', 'total_qty', 'amount', 'seller_discount', 'taxes', 'total_amount', 'invoice_number', 'payment_status', 'status')
		export_order = ('id', 'invoice_number', 'order__id', 'order__order_number', 'created_date', 'total_qty', 'amount', 'seller_discount', 'taxes', 'total_amount', 'invoice_number', 'payment_status', 'status')

	def dehydrate_created_date(self, obj):
		try:
			return timezone.localtime(obj.datetime).strftime("%Y-%m-%d %H:%M:%S") #.strftime("%B %d, %Y, %I:%M%p")
		except:
			return ''

InvoiceForm = select2_modelform(Invoice, attrs={'width': '250px'})
class InvoiceAdmin(ExportMixin, admin.ModelAdmin):
	list_display = ('id', 'invoice_number', 'order_detail', 'datetime', 'total_qty', 'amount', 'seller_discount', 'taxes', 'total_amount', 'invoice_number', 'payment_status', 'status')
	list_filter = ('status', 'payment_status', ('datetime', DateRangeFilter))
	search_fields = ('id', 'invoice_number', 'order__id', 'order__order_number', 'order__user__username', 'total_qty', 'amount', 'seller_discount', 'taxes', 'total_amount', 'invoice_number')
	raw_id_fields = ('order',)
	form = InvoiceForm
	raw_id_fields = ('order',)
	inlines = (InvoiceItemInline,)#PaymentInline
	exclude = ("invoice", )
	resource_class = InvoiceResource
	readonly_fields = ('created', 'modified',)

	def get_queryset(self, request):
	    return super(InvoiceAdmin, self).get_queryset(request).select_related('order')

	def order_detail(self, obj):
		if obj.order:
			return '<a href="%s" target="_blank">%s</a>' % ("/api/admin/api/salesorder/"+str(obj.order.id), obj.order)
		return None
	order_detail.allow_tags = True
	order_detail.short_description = 'Order'
	order_detail.admin_order_field = 'order_id'

admin.site.register(Invoice, InvoiceAdmin)

InvoiceItemForm = select2_modelform(InvoiceItem, attrs={'width': '250px'})
class InvoiceItemAdmin(admin.ModelAdmin):
	list_display = ('id', 'invoice', 'order_item', 'qty', )
	search_fields = ('id', 'invoice__id', 'order_item__id', 'qty', )
	form = InvoiceItemForm
	raw_id_fields = ('invoice', 'order_item')

	def get_queryset(self, request):
	    return super(InvoiceItemAdmin, self).get_queryset(request).select_related('invoice__order','order_item')

admin.site.register(InvoiceItem, InvoiceItemAdmin)

PaymentForm = select2_modelform(Payment, attrs={'width': '250px'})
class PaymentAdmin(admin.ModelAdmin):
	list_display = ('id', 'by_compny', 'to_compny', 'amount', 'status', 'mode', 'invoices', 'datetime', 'modified',)
	search_fields = ('id', 'by_company__name', 'to_company__name', 'amount', 'mode', 'invoice__id')
	list_filter = ('status', ('datetime', DateRangeFilter))
	form = PaymentForm
	raw_id_fields = ('by_company', 'to_company', 'user', 'invoice')
	readonly_fields = ('created', 'modified',)

	def get_queryset(self, request):
	    return super(PaymentAdmin, self).get_queryset(request).select_related('by_company','to_company').prefetch_related('invoice')

	def invoices(self, obj):
	    try:
		# ~ ids = obj.invoice.all().values_list('id', flat=True).distinct()
		# ~ ids = map(str, ids)
		# ~ return ', '.join(ids)
		ids = []
		invoices = obj.invoice.all()
		for inv in invoices:
		    #ids.append(inv.id)
		    ids.append('<a href="%s" target="_blank">%s</a>' % ("/api/admin/api/invoice/"+str(inv.id), inv.id))
		ids = map(str,ids)
		return ', '.join(list(ids))
	    except:
		return ""
	invoices.allow_tags = True
	invoices.short_description = 'Invoices'

	def by_compny(self, obj):
		if obj.by_company:
			return '<a href="%s" target="_blank">%s</a>' % ("/api/admin/api/company/"+str(obj.by_company.id), obj.by_company)
		return None
	by_compny.allow_tags = True
	by_compny.short_description = 'By Company'
	by_compny.admin_order_field = 'by_company_id'

	def to_compny(self, obj):
		if obj.to_company:
			return '<a href="%s" target="_blank">%s</a>' % ("/api/admin/api/company/"+str(obj.to_company.id), obj.to_company)
		return None
	to_compny.allow_tags = True
	to_compny.short_description = 'To Company'
	to_compny.admin_order_field = 'to_company_id'

admin.site.register(Payment, PaymentAdmin)

'''PaymentInvoiceForm = select2_modelform(PaymentInvoice, attrs={'width': '250px'})
class PaymentInvoiceAdmin(admin.ModelAdmin):
	list_display = ('id', 'datetime', 'invoice', 'amount', )
	search_fields = ('id', 'datetime', 'invoice', 'amount', )
	form = PaymentInvoiceForm
	raw_id_fields = ('invoice',)

	def get_queryset(self, request):
	    return super(PaymentInvoiceAdmin, self).get_queryset(request).select_related('invoice')

admin.site.register(PaymentInvoice, PaymentInvoiceAdmin)'''

ShipmentForm = select2_modelform(Shipment, attrs={'width': '250px'})
class ShipmentAdmin(admin.ModelAdmin):
	list_display = ('id', 'invoice', 'datetime', 'tracking_number', 'logistics_provider', 'created', 'modified',)
	search_fields = ('id', 'invoice__id', 'invoice__invoice_number', 'datetime', 'tracking_number', 'logistics_provider',)
	form = ShipmentForm
	raw_id_fields = ('invoice',)
	readonly_fields = ('created', 'modified',)

	def get_queryset(self, request):
	    return super(ShipmentAdmin, self).get_queryset(request).select_related('invoice__order')

admin.site.register(Shipment, ShipmentAdmin)

UserSendNotificationForm = select2_modelform(UserSendNotification, attrs={'width': '250px'})
class UserSendNotificationAdmin(admin.ModelAdmin):
	list_display = ('id', 'user', 'created_at', 'send_sms', 'send_chat', 'send_gcm',)
	list_filter = (('created_at', DateRangeFilter),)
	search_fields = ('id', 'user__username', 'created_at', 'send_sms', 'send_chat', 'send_gcm',)
	form = UserSendNotificationForm
	raw_id_fields = ('user',)

	def get_queryset(self, request):
	    return super(UserSendNotificationAdmin, self).get_queryset(request).select_related('user')

admin.site.register(UserSendNotification, UserSendNotificationAdmin)

class CompanyCatalogViewResource(resources.ModelResource):
	phone_number = fields.Field()
	class Meta:
		model = CompanyCatalogView
		skip_unchanged = True
		report_skipped = False
		fields = ('id', 'company__id', 'company__name', 'user__username', 'phone_number', 'catalog__id', 'catalog__title', 'catalog__category__id', 'catalog__category__category_name', 'catalog_type', 'clicks', 'created_at',)
		export_order = ('id', 'company__id', 'company__name', 'user__username', 'phone_number', 'catalog__id', 'catalog__title', 'catalog__category__id', 'catalog__category__category_name', 'catalog_type', 'clicks', 'created_at',)

	def dehydrate_phone_number(self, obj):
	    #return obj.company.phone_number
	    if obj.company:
		return obj.company.phone_number
	    elif obj.user:
		return obj.user.userprofile.phone_number
	    else:
		return ""

CompanyCatalogViewForm = select2_modelform(CompanyCatalogView, attrs={'width': '250px'})
class CompanyCatalogViewAdmin(ExportMixin, admin.ModelAdmin):
	list_display = ('id', 'company', 'user', 'phone_number', 'catalog', 'catalog_type', 'clicks', 'created_at',)
	list_filter = ('created_at', ('created_at', DateRangeFilter),)
	search_fields = ('id', 'company__name', 'user__username', 'company__phone_number', 'catalog__title', 'catalog_type', 'clicks', 'created_at',)
	form = CompanyCatalogViewForm
	raw_id_fields = ('company', 'catalog', 'user')
	resource_class = CompanyCatalogViewResource

	def get_queryset(self, request):
	    return super(CompanyCatalogViewAdmin, self).get_queryset(request).select_related('company','catalog','user__userprofile')

	def phone_number(self, obj):
	    if obj.company:
		return obj.company.phone_number
	    elif obj.user:
		return obj.user.userprofile.phone_number
	    else:
		return ""
	phone_number.admin_order_field = 'company__phone_number'

admin.site.register(CompanyCatalogView, CompanyCatalogViewAdmin)

class CompanyProductViewResource(resources.ModelResource):

	class Meta:
		model = CompanyProductView
		skip_unchanged = True
		report_skipped = False
		fields = ('id', 'company', 'product', 'created_at',)
		export_order = ('id', 'company', 'product', 'created_at',)

CompanyProductViewForm = select2_modelform(CompanyProductView, attrs={'width': '250px'})
class CompanyProductViewAdmin(ExportMixin, admin.ModelAdmin):
	list_display = ('id', 'company', 'product', 'created_at',)
	list_filter = ('created_at', ('created_at', DateRangeFilter),)
	search_fields = ('id', 'company__name', 'product__title', 'created_at',)
	form = CompanyProductViewForm
	raw_id_fields = ('company', 'product')
	resource_class = CompanyProductViewResource

	def get_queryset(self, request):
	    return super(CompanyProductViewAdmin, self).get_queryset(request).select_related('company','product')

admin.site.register(CompanyProductView, CompanyProductViewAdmin)


JobsForm = select2_modelform(Jobs, attrs={'width': '250px'})
class JobsAdmin(admin.ModelAdmin):
	list_display = ('id', 'user', 'company', 'job_type', 'status', 'created_at', 'total_rows', 'completed_rows', 'error_details', 'exception_details')
	list_filter = ('job_type', 'status', ('created_at', DateRangeFilter),)
	search_fields = ('id', 'user__username', 'company__name', 'job_type', 'status', 'created_at', 'total_rows', 'completed_rows', 'error_details', 'exception_details')
	form = JobsForm
	raw_id_fields = ('company', 'user')
	actions = ['task_restart']

	def get_queryset(self, request):
	    return super(JobsAdmin, self).get_queryset(request).select_related('company','user')

	def task_restart(self, request, queryset):
	    ids = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
	    print ids
	    jobObjs = Jobs.objects.filter(id__in=ids)
	    for jobObj in jobObjs:
		import time
		time.sleep(1) #in second
		jobObj.completed_rows = 0
		jobObj.error_details = None
		jobObj.exception_details = None
		jobObj.status = "Scheduled"
		jobObj.error_file = None
		jobObj.save()
		if jobObj.job_type == "Buyer":
		    if settings.TASK_QUEUE_METHOD == 'celery':
			    task_id = buyerCSVImportJobs.apply_async((jobObj.id,), expires=datetime.now() + timedelta(days=2))
		    elif settings.TASK_QUEUE_METHOD == 'djangoQ':
			    task_id = async(
				    'api.tasks.buyerCSVImportJobs',
				    jobObj.id,
				    broker = priority_broker
			    )
		    print task_id
		elif jobObj.job_type == "Supplier":
		    if settings.TASK_QUEUE_METHOD == 'celery':
			    task_id = supplierCSVImportJobs.apply_async((jobObj.id,), expires=datetime.now() + timedelta(days=2))
		    elif settings.TASK_QUEUE_METHOD == 'djangoQ':
			    task_id = async(
				    'api.tasks.supplierCSVImportJobs',
				    jobObj.id,
				    broker = priority_broker
			    )
		    print task_id
		elif jobObj.job_type == "Sales Order CSV":
		    if settings.TASK_QUEUE_METHOD == 'celery':
			    task_id = salesOrderCSVImportJobs.apply_async((jobObj.id,), expires=datetime.now() + timedelta(days=2))
		    elif settings.TASK_QUEUE_METHOD == 'djangoQ':
			    task_id = async(
				    'api.tasks.salesOrderCSVImportJobs',
				    jobObj.id,
				    broker = priority_broker
			    )
		    print task_id
		elif jobObj.job_type == "Shipment Sales Order CSV":
		    if settings.TASK_QUEUE_METHOD == 'celery':
			    task_id = shipmentCSVImportJobs.apply_async((jobObj.id,), expires=datetime.now() + timedelta(days=2))
		    elif settings.TASK_QUEUE_METHOD == 'djangoQ':
			    task_id = async(
				    'api.tasks.shipmentCSVImportJobs',
				    jobObj.id,
				    broker = priority_broker
			    )
		    print task_id
		elif jobObj.job_type == "SKU Map CSV":
		    if settings.TASK_QUEUE_METHOD == 'celery':
			    task_id = skuMapCSVImportJobs.apply_async((jobObj.id,), expires=datetime.now() + timedelta(days=2))
		    elif settings.TASK_QUEUE_METHOD == 'djangoQ':
			    task_id = async(
				    'api.tasks.skuMapCSVImportJobs',
				    jobObj.id,
				    broker = priority_broker
			    )
		    print task_id
		elif jobObj.job_type == "Company Map CSV":
		    if settings.TASK_QUEUE_METHOD == 'celery':
			    task_id = companyMapCSVImportJobs.apply_async((jobObj.id,), expires=datetime.now() + timedelta(days=2))
		    elif settings.TASK_QUEUE_METHOD == 'djangoQ':
			    task_id = async(
				    'api.tasks.companyMapCSVImportJobs',
				    jobObj.id,
				    broker = priority_broker
			    )
		    print task_id
		elif jobObj.job_type == "Catalog CSV":
		    if settings.TASK_QUEUE_METHOD == 'celery':
			    task_id = catalogCSVImportJobs.apply_async((jobObj.id,), expires=datetime.now() + timedelta(days=2))
		    elif settings.TASK_QUEUE_METHOD == 'djangoQ':
			    task_id = async(
				    'api.tasks.catalogCSVImportJobs',
				    jobObj.id,
				    broker = priority_broker
			    )
		    print task_id
		elif jobObj.job_type == "Product CSV":
		    if settings.TASK_QUEUE_METHOD == 'celery':
			    task_id = productCSVImportJobs.apply_async((jobObj.id,), expires=datetime.now() + timedelta(days=2))
		    elif settings.TASK_QUEUE_METHOD == 'djangoQ':
			    task_id = async(
				    'api.tasks.productCSVImportJobs',
				    jobObj.id,
				    broker = priority_broker
			    )
		    print task_id
		elif jobObj.job_type == "Shipment Dispatch CSV":
		    if settings.TASK_QUEUE_METHOD == 'celery':
			    task_id = shipmentDispatchCSVImportJobs.apply_async((jobObj.id,), expires=datetime.now() + timedelta(days=2))
		    elif settings.TASK_QUEUE_METHOD == 'djangoQ':
			    task_id = async(
				    'api.tasks.shipmentDispatchCSVImportJobs',
				    jobObj.id,
				    broker = priority_broker
			    )
		    print task_id
	    messages.success(request, 'task started successfully')
	    return
	task_restart.short_description = u'Restart Task'

admin.site.register(Jobs, JobsAdmin)

PushSellerPriceForm = select2_modelform(PushSellerPrice, attrs={'width': '250px'})
class PushSellerPriceAdmin(admin.ModelAdmin):
	list_display = ('id', 'push', 'selling_company', 'product', 'price', 'created_at')
	list_filter = ('created_at', ('created_at', DateRangeFilter),)
	search_fields = ('id', 'push__id', 'selling_company__name', 'product__title', 'price', )
	form = PushSellerPriceForm
	raw_id_fields = ('push', 'selling_company', 'product')

	def get_queryset(self, request):
	    return super(PushSellerPriceAdmin, self).get_queryset(request).select_related('selling_company','push', 'product')

admin.site.register(PushSellerPrice, PushSellerPriceAdmin)

PromotionForm = select2_modelform(Promotion, attrs={'width': '250px'})
class PromotionAdmin(admin.ModelAdmin):
	list_display = ('id', 'landing_page_type', 'landing_page', 'start_date', 'end_date', 'status', 'active', 'show_on_webapp', 'manufacturer', 'wholesaler', 'retailer', 'broker', 'languages')
	list_filter = ('status', 'start_date', ('start_date', DateRangeFilter),)
	search_fields = ('id', 'landing_page_type', 'landing_page', 'start_date', 'end_date', 'status', 'active', 'show_on_webapp', 'language__name')
	form = PromotionForm
	readonly_fields = ('created', 'modified',)

	def save_model(self, request, obj, form, change):
	    messages.add_message(request, messages.INFO, 'Promotion has been created !!!')
	    super(PromotionAdmin, self).save_model(request, obj, form, change)

	def languages(self, obj):
	    try:
		name = obj.language.all().values_list('name', flat=True).distinct()

		return ', '.join(name)

	    except:
		return ""

admin.site.register(Promotion, PromotionAdmin)

SalesmanLocationForm = select2_modelform(SalesmanLocation, attrs={'width': '250px'})
class SalesmanLocationAdmin(admin.ModelAdmin):
	list_display = ('id', 'salesman',)
	search_fields = ('id', 'salesman__username',)
	form = SalesmanLocationForm
	raw_id_fields = ('salesman',)
	filter_horizontal = ('state', 'city')

admin.site.register(SalesmanLocation, SalesmanLocationAdmin)

BuyerSalesmenForm = select2_modelform(BuyerSalesmen, attrs={'width': '250px'})
class BuyerSalesmenAdmin(admin.ModelAdmin):
	list_display = ('id', 'salesman')
	search_fields = ('id', 'salesman__username')
	form = BuyerSalesmenForm
	raw_id_fields = ('buyers','salesman')

admin.site.register(BuyerSalesmen, BuyerSalesmenAdmin)

AssignGroupsForm = select2_modelform(AssignGroups, attrs={'width': '250px'})
class AssignGroupsAdmin(admin.ModelAdmin):
	list_display = ('id', 'user')
	search_fields = ('id', 'user__username')
	form = AssignGroupsForm
	#filter_horizontal = ('groups',)
	raw_id_fields = ('user','groups',)

admin.site.register(AssignGroups, AssignGroupsAdmin)

CatalogUploadOptionForm = select2_modelform(CatalogUploadOption, attrs={'width': '250px'})
class CatalogUploadOptionAdmin(admin.ModelAdmin):
	list_display = ('id', 'catalog')
	search_fields = ('id', 'catalog__title')
	form = CatalogUploadOptionForm
	#filter_horizontal = ('groups',)
	raw_id_fields = ('catalog',)
	readonly_fields = ('created', 'modified',)

admin.site.register(CatalogUploadOption, CatalogUploadOptionAdmin)


class CompanyKycTaxationResource(resources.ModelResource):
    class Meta:
	    model = CompanyKycTaxation
	    skip_unchanged = True
	    report_skipped = True
	    skip_row = True
	    fields = ('id', 'company', 'pan', 'gstin', 'arn', 'add_gst_to_price', 'company_type', 'is_completed')
	    #exclude = ('id', )
	    import_id_fields = ('id', )
    def skip_row(self, instance, original):
        allfields = list(self.get_fields())

	#for field in allfields:
	#    print field.get_value(instance)

	allfields0 = allfields[0].get_value(instance)
	allfields1 = allfields[1].get_value(instance)
	allfields2 = allfields[2].get_value(instance)
	allfields2 = allfields[3].get_value(instance)
	allfields2 = allfields[4].get_value(instance)
	allfields2 = allfields[5].get_value(instance)
	allfields2 = allfields[6].get_value(instance)
	allfields2 = allfields[7].get_value(instance)

	if CompanyKycTaxation.objects.filter(company=allfields1).exclude(id=allfields0).exists():
	    return True

        if not self._meta.skip_unchanged:
            return False
        for field in self.get_fields():
            try:
                # For fields that are models.fields.related.ManyRelatedManager
                # we need to compare the results
                if list(field.get_value(instance).all()) != list(field.get_value(original).all()):
                    return False
            except AttributeError:
                if field.get_value(instance) != field.get_value(original):
                    return False
        return True


CompanyKycTaxationForm = select2_modelform(CompanyKycTaxation, attrs={'width': '250px'})
class CompanyKycTaxationAdmin(ImportExportModelAdmin, admin.ModelAdmin):
	list_display = ('id', 'company', 'pan', 'gstin', 'arn', 'add_gst_to_price', 'created', 'modified',)
	search_fields = ('id', 'company__name', 'pan', 'gstin', 'arn', 'add_gst_to_price')
	form =CompanyKycTaxationForm
	#filter_horizontal = ('groups',)
	raw_id_fields = ('company',)
	resource_class = CompanyKycTaxationResource
	readonly_fields = ('created', 'modified',)

admin.site.register(CompanyKycTaxation, CompanyKycTaxationAdmin)


class SolePropreitorshipKYCResource(resources.ModelResource):
    class Meta:
	    model = SolePropreitorshipKYC
	    skip_unchanged = True
	    report_skipped = True
	    skip_row = True
	    fields = ('id', 'company', 'full_name', 'father_name', 'spouse_name', 'birth_date', 'gender', 'email', 'mobile_no', 'pan_card', 'aadhar_card', 'address', 'pincode', 'state', 'city')
	    #exclude = ('id', )
	    import_id_fields = ('id', )
    def skip_row(self, instance, original):
        allfields = list(self.get_fields())

	#for field in allfields:
	#    print field.get_value(instance)

	allfields0 = allfields[0].get_value(instance)
	allfields1 = allfields[1].get_value(instance)
	allfields2 = allfields[2].get_value(instance)

	if SolePropreitorshipKYC.objects.filter(company=allfields1).exclude(id=allfields0).exists():
	    return True

        if not self._meta.skip_unchanged:
            return False
        for field in self.get_fields():
            try:
                # For fields that are models.fields.related.ManyRelatedManager
                # we need to compare the results
                if list(field.get_value(instance).all()) != list(field.get_value(original).all()):
                    return False
            except AttributeError:
                if field.get_value(instance) != field.get_value(original):
                    return False
        return True

class SolePropreitorshipKYCAdmin(ImportExportModelAdmin, admin.ModelAdmin):
	list_display = ('id', 'company', 'full_name', 'birth_date', 'gender', 'email', 'mobile_no', 'pan_card', 'aadhar_card', 'pincode', 'state', 'city', 'created', 'modified',)
	search_fields = ('id', 'company__name', 'full_name', 'birth_date', 'gender', 'email', 'mobile_no', 'pan_card', 'aadhar_card', 'pincode', 'state', 'city')
	form =CompanyKycTaxationForm
	#filter_horizontal = ('groups',)
	raw_id_fields = ('company',)
	resource_class = SolePropreitorshipKYCResource
	readonly_fields = ('created', 'modified',)

admin.site.register(SolePropreitorshipKYC, SolePropreitorshipKYCAdmin)

class CompanyCreditRatingResource(resources.ModelResource):
    class Meta:
	    model = CompanyCreditRating
	    skip_unchanged = True
	    report_skipped = True
	    skip_row = True
	    fields = ('id', 'company', 'bureau_score', 'bank_data_source', 'bank_statement_pdf', 'bank_monthly_transaction_6m', 'bank_average_balance_6m', 'bank_check_bounces_6m', 'salary', 'gst_credit_rating', 'average_payment_duration', 'average_gr_rate', 'rating', 'bureau_report_rating', 'financial_statement_rating')
	    #exclude = ('id', )
	    import_id_fields = ('id', )
    def skip_row(self, instance, original):
        allfields = list(self.get_fields())

	#for field in allfields:
	#    print field.get_value(instance)

	allfields0 = allfields[0].get_value(instance)
	allfields1 = allfields[1].get_value(instance)
	allfields2 = allfields[2].get_value(instance)

	if CompanyCreditRating.objects.filter(company=allfields1).exclude(id=allfields0).exists():
	    return True

        if not self._meta.skip_unchanged:
            return False
        for field in self.get_fields():
            try:
                # For fields that are models.fields.related.ManyRelatedManager
                # we need to compare the results
                if list(field.get_value(instance).all()) != list(field.get_value(original).all()):
                    return False
            except AttributeError:
                if field.get_value(instance) != field.get_value(original):
                    return False
        return True

class CompanyCreditRatingAdmin(ImportExportModelAdmin, admin.ModelAdmin):
	list_display = ('id', 'company', 'rating', 'bureau_score', 'gst_credit_rating', 'created', 'modified',)
	search_fields = ('id', 'company__name', 'rating', 'bureau_score', 'gst_credit_rating')
	form =CompanyKycTaxationForm
	#filter_horizontal = ('groups',)
	raw_id_fields = ('company',)
	resource_class = CompanyCreditRatingResource
	readonly_fields = ('created', 'modified',)

admin.site.register(CompanyCreditRating, CompanyCreditRatingAdmin)


class UserCreditSubmissionAdmin(admin.ModelAdmin):
	list_display = ('id', 'company', 'rating', 'bureau_score', 'gst_credit_rating', 'created')
	search_fields = ('id', 'company__name', 'rating', 'bureau_score', 'gst_credit_rating')
	form =CompanyKycTaxationForm
	#filter_horizontal = ('groups',)
	raw_id_fields = ('company','user')
	readonly_fields = ('created', )

admin.site.register(UserCreditSubmission, UserCreditSubmissionAdmin)

class CreditReferenceResource(resources.ModelResource):
    class Meta:
	    model = CreditReference
	    skip_unchanged = True
	    report_skipped = True
	    skip_row = True
	    fields = ('id', 'selling_company', 'buying_company', 'transaction_on_credit', 'number_transactions', 'transaction_value', 'average_payment_duration', 'average_gr_rate', 'remarks')
	    #exclude = ('id', )
	    import_id_fields = ('id', )
    def skip_row(self, instance, original):
        allfields = list(self.get_fields())

	#for field in allfields:
	#    print field.get_value(instance)

	allfields0 = allfields[0].get_value(instance)
	allfields1 = allfields[1].get_value(instance)
	allfields2 = allfields[2].get_value(instance)

	if CreditReference.objects.filter(selling_company=allfields1, buying_company=allfields2).exclude(id=allfields0).exists():
	    return True

        if not self._meta.skip_unchanged:
            return False
        for field in self.get_fields():
            try:
                # For fields that are models.fields.related.ManyRelatedManager
                # we need to compare the results
                if list(field.get_value(instance).all()) != list(field.get_value(original).all()):
                    return False
            except AttributeError:
                if field.get_value(instance) != field.get_value(original):
                    return False
        return True

class CreditReferenceAdmin(ImportExportModelAdmin, admin.ModelAdmin):
	list_display = ('id', 'selling_company', 'buying_company', 'transaction_value', 'average_payment_duration', 'average_gr_rate', 'created', 'modified',)
	search_fields = ('id', 'selling_company__name', 'buying_company__name', 'transaction_value', 'average_payment_duration', 'average_gr_rate')
	form =CompanyKycTaxationForm
	#filter_horizontal = ('groups',)
	raw_id_fields = ('selling_company', 'buying_company',)
	resource_class = CreditReferenceResource

admin.site.register(CreditReference, CreditReferenceAdmin)



TaxTypeForm = select2_modelform(TaxType, attrs={'width': '250px'})
class TaxTypeAdmin(admin.ModelAdmin):
	list_display = ('id', 'name', 'created', 'modified',)
	search_fields = ('id', 'name')
	form =TaxTypeForm
	readonly_fields = ('created', 'modified',)

admin.site.register(TaxType, TaxTypeAdmin)

TaxCodeForm = select2_modelform(TaxCode, attrs={'width': '250px'})
class TaxCodeAdmin(admin.ModelAdmin):
	list_display = ('id', 'tax_type', 'tax_code', 'tax_code_type', 'created', 'modified',)
	search_fields = ('id', 'tax_type__name', 'tax_code', 'tax_code_type')
	form =TaxCodeForm
	readonly_fields = ('created', 'modified',)
	#filter_horizontal = ('groups',)
	#raw_id_fields = ('tax_type',)

admin.site.register(TaxCode, TaxCodeAdmin)

class TaxClassResource(resources.ModelResource):
    class Meta:
	    model = TaxClass
	    skip_unchanged = True
	    report_skipped = True
	    skip_row = True
	    fields = ('id', 'tax_code', 'tax_name', 'from_price', 'to_price', 'location_type', 'percentage')
	    #exclude = ('id', )
	    import_id_fields = ('id', )
    def skip_row(self, instance, original):
        allfields = list(self.get_fields())

	#for field in allfields:
	#    print field.get_value(instance)

	allfields0 = allfields[0].get_value(instance)
	allfields1 = allfields[1].get_value(instance)
	allfields2 = allfields[2].get_value(instance)
	allfields3 = allfields[3].get_value(instance)
	allfields4 = allfields[4].get_value(instance)
	allfields5 = allfields[5].get_value(instance)
	allfields6 = allfields[6].get_value(instance)

	if TaxClass.objects.filter(tax_code=allfields1, tax_name=allfields2, from_price=allfields3, to_price=allfields4, location_type=allfields5, percentage=allfields6).exists():
	    return True

        if not self._meta.skip_unchanged:
            return False
        for field in self.get_fields():
            try:
                # For fields that are models.fields.related.ManyRelatedManager
                # we need to compare the results
                if list(field.get_value(instance).all()) != list(field.get_value(original).all()):
                    return False
            except AttributeError:
                if field.get_value(instance) != field.get_value(original):
                    return False
        return True

TaxClassForm = select2_modelform(TaxClass, attrs={'width': '250px'})
class TaxClassAdmin(ImportExportModelAdmin, admin.ModelAdmin):
	list_display = ('id', 'tax_code', 'tax_name', 'from_price', 'to_price', 'location_type', 'percentage', 'created', 'modified',)
	search_fields = ('id', 'tax_code__tax_code', 'from_price', 'to_price', 'tax_name', 'location_type', 'percentage')
	form =TaxClassForm
	#filter_horizontal = ('groups',)
	#raw_id_fields = ('tax_type',)
	resource_class = TaxClassResource
	readonly_fields = ('created', 'modified',)

admin.site.register(TaxClass, TaxClassAdmin)

CategoryTaxClassForm = select2_modelform(CategoryTaxClass, attrs={'width': '250px'})
class CategoryTaxClassAdmin(admin.ModelAdmin):
	list_display = ('id', 'category', 'created', 'modified',)
	search_fields = ('id', 'category__category_name')
	form =CategoryTaxClassForm
	filter_horizontal = ('tax_classes',)
	readonly_fields = ('created', 'modified',)
	#raw_id_fields = ('tax_type',)

admin.site.register(CategoryTaxClass, CategoryTaxClassAdmin)

class PaidClientAdmin(admin.ModelAdmin):
	list_display = ('id', 'company')
	search_fields = ('id', 'company__name')
	raw_id_fields = ('company',)

admin.site.register(PaidClient, PaidClientAdmin)

class OrderRatingResource(resources.ModelResource):
    class Meta:
	    model = OrderRating
	    skip_unchanged = True
	    report_skipped = True
	    skip_row = True
	    fields = ('id', 'order', 'seller_rating', 'buyer_rating')
	    export_order = ('id', 'order', 'seller_rating', 'buyer_rating')
	    import_id_fields = ('id', )
    def skip_row(self, instance, original):
        allfields = list(self.get_fields())

	#for field in allfields:
	#    print field.get_value(instance)

	allfields0 = allfields[0].get_value(instance)
	allfields1 = allfields[1].get_value(instance)
	allfields2 = allfields[2].get_value(instance)
	allfields3 = allfields[3].get_value(instance)
	#~ allfields4 = allfields[4].get_value(instance)
	#~ allfields5 = allfields[5].get_value(instance)
	#~ allfields6 = allfields[6].get_value(instance)

	if OrderRating.objects.filter(order=allfields1, seller_rating=allfields2, buyer_rating=allfields3).exists() or OrderRating.objects.filter(order=allfields1).exclude(id=allfields0).exists():
	    return True

        if not self._meta.skip_unchanged:
            return False
        for field in self.get_fields():
            try:
                # For fields that are models.fields.related.ManyRelatedManager
                # we need to compare the results
                if list(field.get_value(instance).all()) != list(field.get_value(original).all()):
                    return False
            except AttributeError:
                if field.get_value(instance) != field.get_value(original):
                    return False
        return True

class OrderRatingAdmin(ImportExportModelAdmin, admin.ModelAdmin):
	list_display = ('id', 'order', 'seller', 'buyer', 'seller_rating', 'buyer_rating', 'created', 'modified',)
	search_fields = ('id', 'order__order_number', 'order__seller_company__name', 'order__company__name', 'seller_rating', 'buyer_rating')
	raw_id_fields = ('order',)
	resource_class = OrderRatingResource
	readonly_fields = ('created', 'modified',)

	def seller(self, obj):
	    try:
		return obj.order.seller_company.name
	    except:
		return ""

	def buyer(self, obj):
	    try:
		return obj.order.company.name
	    except:
		return ""

admin.site.register(OrderRating, OrderRatingAdmin)

class CompanyRatingAdmin(admin.ModelAdmin):
	list_display = ('id', 'company', 'seller_score', 'buyer_score', 'created', 'modified',)
	search_fields = ('id', 'company__name', 'seller_score', 'buyer_score')
	raw_id_fields = ('company',)
	readonly_fields = ('created', 'modified',)

admin.site.register(CompanyRating, CompanyRatingAdmin)


class CompanyBrandFollowResource(resources.ModelResource):
	class Meta:
		model = CompanyBrandFollow
		skip_unchanged = True
		report_skipped = False
		fields = ('id', 'brand__name', 'company__name', 'user__username',)
		export_order = ('id', 'brand__name', 'company__name', 'user__username',)

class CompanyBrandFollowAdmin(ExportMixin, admin.ModelAdmin):
	list_display = ('id', 'brand', 'company', 'user', 'created', 'modified',)
	search_fields = ('id', 'brand__name', 'company__name', 'user__username')
	raw_id_fields = ('brand','company', 'user')
	resource_class = CompanyBrandFollowResource
	readonly_fields = ('created', 'modified',)

admin.site.register(CompanyBrandFollow, CompanyBrandFollowAdmin)

class ApprovedCreditAdmin(admin.ModelAdmin):
	list_display = ('id', 'company', 'total_limit', 'lender_company')
	search_fields = ('id', 'company__name', 'total_limit', 'lender_company')
	raw_id_fields = ('company',)
	readonly_fields = ('created', 'modified',)

admin.site.register(ApprovedCredit, ApprovedCreditAdmin)

class LoanAdmin(admin.ModelAdmin):
	list_display = ('id', 'company', 'status')
	search_fields = ('id', 'company__name', 'status')
	raw_id_fields = ('company',)

admin.site.register(Loan, LoanAdmin)

class PaymentMethodAdmin(admin.ModelAdmin):
	list_display = ('id', 'name', 'payment_type', 'display_name', 'status')
	search_fields = ('id', 'name', 'payment_type', 'display_name', 'status')

admin.site.register(PaymentMethod, PaymentMethodAdmin)

class ConfigAdmin(admin.ModelAdmin):
	list_display = ('id', 'key', 'value', 'visible_on_frontend')
	search_fields = ('id', 'key', 'value', 'visible_on_frontend')
	readonly_fields = ('created', 'modified',)

admin.site.register(Config, ConfigAdmin)

class AddressResource(resources.ModelResource):
	company = fields.Field()
	company_types = fields.Field()

	user_number = fields.Field()
	company_number = fields.Field()

	class Meta:
		model = Address
		skip_unchanged = True
		report_skipped = False
		fields = ('id', 'user__username', 'user_number', 'company', 'company_number', 'name', 'city__city_name', 'state__state_name', 'pincode', 'latitude', 'longitude', 'company_types', 'location_address', 'location_city', 'location_state')
		export_order = ('id', 'user__username', 'user_number', 'company', 'company_number', 'name', 'city__city_name', 'state__state_name', 'pincode', 'latitude', 'longitude', 'company_types', 'location_address', 'location_city', 'location_state')

	def get_queryset(self, request):
	    return super(AddressResource, self).get_queryset(request).select_related('city', 'state', 'user__companyuser__company__company_group_flag', 'user__userprofile').order_by('-id')

	def dehydrate_user_number(self, obj):
		try:
			return obj.user.userprofile.phone_number
		except:
			return ""

	def dehydrate_company(self, obj):
		try:
			global companyObj
			companyObj = obj.user.companyuser.company
			return companyObj.name
		except:
			return ""

	def dehydrate_company_number(self, obj):
		try:
			global companyObj
			return companyObj.phone_number
		except:
			return ""

	def dehydrate_company_types(self, obj):
		try:
			global companyObj
			#ct = CompanyType.objects.get(company=companyObj)
			ct = companyObj.company_group_flag
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

			return arr
		except:
			return ""

class AddressAdmin(ExportMixin, admin.ModelAdmin):
	list_display = ('id', 'user', 'company', 'name', 'city', 'state', 'pincode', 'latitude', 'longitude', 'company_types', 'location_address')
	search_fields = ('id', 'user__username', 'user__companyuser__company__name', 'name', 'city__city_name', 'state__state_name', 'pincode', 'latitude', 'longitude', 'location_address')
	raw_id_fields = ('user', 'city', 'state',)
	resource_class = AddressResource
	readonly_fields = ('created', 'modified',)

	def get_queryset(self, request):
	    return super(AddressAdmin, self).get_queryset(request).select_related('city', 'state', 'user__companyuser__company__company_group_flag').order_by('-id')

	def company(self, obj):
	    try:
		global companyObj
		companyObj = obj.user.companyuser.company
		return companyObj.name
	    except:
		return ""

	def company_types(self, obj):
	    try:
		global companyObj
		#ct = CompanyType.objects.get(company=companyObj)
		ct = companyObj.company_group_flag
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

		return arr
	    except:
		return ""

admin.site.register(Address, AddressAdmin)

class PincodeZoneResource(resources.ModelResource):
    class Meta:
	    model = PincodeZone
	    skip_unchanged = True
	    report_skipped = True
	    skip_row = True
	    fields = ('id', 'pincode', 'zone', 'city', 'is_servicable', 'cod_available',)
	    #exclude = ('id', )
	    import_id_fields = ('id', )
    def skip_row(self, instance, original):
        allfields = list(self.get_fields())

	#for field in allfields:
	#    print field.get_value(instance)

	allfields0 = allfields[0].get_value(instance)
	allfields1 = allfields[1].get_value(instance)
	allfields2 = allfields[2].get_value(instance)
	allfields3 = allfields[3].get_value(instance)
	allfields4 = allfields[4].get_value(instance)
	allfields5 = allfields[5].get_value(instance)

	if PincodeZone.objects.filter(city=allfields1, pincode=allfields2, zone=allfields3, is_servicable=allfields4, cod_available=allfields5).exists():
	    return True

        if not self._meta.skip_unchanged:
            return False
        for field in self.get_fields():
            try:
                # For fields that are models.fields.related.ManyRelatedManager
                # we need to compare the results
                if list(field.get_value(instance).all()) != list(field.get_value(original).all()):
                    return False
            except AttributeError:
                if field.get_value(instance) != field.get_value(original):
                    return False
        return True

class PincodeZoneAdmin(ImportExportModelAdmin, admin.ModelAdmin):
	list_display = ('id', 'pincode', 'zone', 'city', 'is_servicable', 'cod_available', 'created', 'modified',)
	list_filter = ('is_servicable', 'cod_available', 'zone')
	search_fields = ('id', 'pincode', 'zone', 'city__city_name', 'is_servicable', 'cod_available')
	raw_id_fields = ('city',)
	resource_class = PincodeZoneResource
	readonly_fields = ('created', 'modified',)

admin.site.register(PincodeZone, PincodeZoneAdmin)

class UserPlatformInfoAdmin(admin.ModelAdmin):
	list_display = ('id', 'user_detail', 'platform', 'app_version', 'app_version_code', 'device_model', 'brand', 'created', 'modified',)
	search_fields = ('id', 'user__username', 'platform', 'app_version', 'app_version_code', 'device_model', 'brand')
	raw_id_fields = ('user',)
	readonly_fields = ('created', 'modified',)

	def get_queryset(self, request):
	    return super(UserPlatformInfoAdmin, self).get_queryset(request).select_related('user')

	def user_detail(self, obj):
	    return '<a href="%s" target="_blank">%s</a>' % ("/api/admin/auth/user/"+str(obj.user.id), obj.user)
	user_detail.allow_tags = True
	user_detail.short_description = 'User Details'
	user_detail.admin_order_field = 'user__id'

admin.site.register(UserPlatformInfo, UserPlatformInfoAdmin)

class LanguageAdmin(admin.ModelAdmin):
	list_display = ('id', 'name', 'code')
	search_fields = ('id', 'name', 'code')

admin.site.register(Language, LanguageAdmin)

class CompanySellsToStateAdmin(admin.ModelAdmin):
	list_display = ('id', 'company', 'intermediate_buyer', 'state')
	search_fields = ('id', 'company__name', 'intermediate_buyer__name', 'state__state_name')
	raw_id_fields = ('company', 'intermediate_buyer', 'state')

admin.site.register(CompanySellsToState, CompanySellsToStateAdmin)

class CatalogSellerResource(resources.ModelResource):
	total_products = fields.Field()

	class Meta:
		model = CatalogSeller
		skip_unchanged = True
		report_skipped = False
		fields = ('id', 'catalog', 'catalog__title', 'catalog__brand__name', 'selling_company', 'selling_company__name', 'selling_company__phone_number', 'selling_type', 'status', 'total_products', 'expiry_date')
		export_order = ('id', 'catalog', 'catalog__title', 'catalog__brand__name', 'selling_company', 'selling_company__name', 'selling_company__phone_number', 'selling_type', 'status', 'total_products', 'expiry_date')
		widgets = {
		    'expiry_date': {'format': '%B %d, %Y'},
                }

	def dehydrate_total_products(self, obj):
		return Product.objects.filter(catalog=obj.catalog).count()

class CatalogSellerAdmin(ExportMixin, admin.ModelAdmin):
	list_display = ('id', 'catalog_detail', 'selling_compny', 'selling_type', 'status', 'expiry_date', 'created')
	list_filter = ('status', 'selling_type', ('created', DateRangeFilter), ('expiry_date', DateRangeFilter) )
	search_fields = ('id', 'catalog__title', 'selling_company__name')
	raw_id_fields = ('catalog', 'selling_company', 'buyer_segmentation')
	readonly_fields = ('created', 'modified',)

	resource_class = CatalogSellerResource

	def get_queryset(self, request):
	    return super(CatalogSellerAdmin, self).get_queryset(request).select_related('catalog', 'selling_company')

	def catalog_detail(self, obj):
	    return '<a href="%s" target="_blank">%s</a>' % ("/api/admin/api/catalog/"+str(obj.catalog.id), obj.catalog)
	catalog_detail.allow_tags = True
	catalog_detail.short_description = 'Catalog Details'
	catalog_detail.admin_order_field = 'catalog__id'

	def selling_compny(self, obj):
		if obj.selling_company:
			return '<a href="%s" target="_blank">%s</a>' % ("/api/admin/api/company/"+str(obj.selling_company.id), obj.selling_company)
		return None
	selling_compny.allow_tags = True
	selling_compny.short_description = 'Selling Company'
	selling_compny.admin_order_field = 'selling_company_id'

admin.site.register(CatalogSeller, CatalogSellerAdmin)

class UserReviewAdmin(admin.ModelAdmin):
	list_display = ('id', 'reviewimage', 'status', 'languages')
	list_filter = ('status', )
	search_fields = ('id', 'status', 'language__name')

	def reviewimage(self, obj):
	    return '<img border="0" alt="%s" src="%s" width="50" height="50">' % (obj.id, obj.image.thumbnail[settings.SMALL_SQR_IMAGE].url,)
	reviewimage.allow_tags = True
	reviewimage.short_description = 'Image'

	def languages(self, obj):
	    try:
		name = obj.language.all().values_list('name', flat=True).distinct()

		return ', '.join(name)

	    except:
		return ""

admin.site.register(UserReview, UserReviewAdmin)

class PromotionalTagAdmin(admin.ModelAdmin):
	list_display = ('id', 'url', 'status')
	list_filter = ('status', )
	search_fields = ('id', 'url', 'status')
	readonly_fields = ('created', 'modified',)

admin.site.register(PromotionalTag, PromotionalTagAdmin)


class PreDefinedFilterAdmin(admin.ModelAdmin):
	list_display = ('id', 'name', 'category', 'url', 'status',)
	list_filter = ('status', 'category',)
	search_fields = ('id', 'name', 'category', 'status',)
	readonly_fields = ('created', )

admin.site.register(PreDefinedFilter, PreDefinedFilterAdmin)

class UserWishlistAdmin(admin.ModelAdmin):
	list_display = ('id', 'user', 'catalog', 'created')
	search_fields = ('id', 'user__username', 'catalog__title')
	raw_id_fields = ('user', 'catalog')
	readonly_fields = ('created',)

admin.site.register(UserWishlist, UserWishlistAdmin)

class CatalogEAVFlatAdmin(admin.ModelAdmin):
	list_display = ('id', 'catalog', 'fabric_value', 'work_value', 'size_value', 'min_price', 'max_price', 'created_at', 'updated_at')
	list_filter = ('view_permission', 'created_at')
	search_fields = ('id', 'catalog__title', 'fabric_value', 'work_value', 'size_value', 'min_price', 'max_price', 'created_at', 'updated_at')
	raw_id_fields = ('catalog','brand','category')

admin.site.register(CatalogEAVFlat, CatalogEAVFlatAdmin)

class UserContactResource(resources.ModelResource):
    class Meta:
	    model = UserContact
	    skip_unchanged = True
	    report_skipped = False
	    fields = ('id', 'user__username', 'name', 'number', 'created')
	    export_order = ('id', 'user__username', 'name', 'number', 'created')

    def get_queryset(self, request):
	    return super(UserContact, self).get_queryset(request).select_related('user')

class UserContactAdmin(ExportMixin, admin.ModelAdmin):
	list_display = ('id', 'user', 'name', 'number', 'created', 'modified')
	list_filter = ('created', 'modified')
	search_fields = ('id', 'user__username', 'name', 'number', 'created', 'modified')
	raw_id_fields = ('user',)
	resource_class = UserContactResource
	readonly_fields = ('created', 'modified',)

	def get_queryset(self, request):
	    return super(UserContactAdmin, self).get_queryset(request).select_related('user').order_by('-id')


admin.site.register(UserContact, UserContactAdmin)

class SearchQueryAdmin(admin.ModelAdmin):
	list_display = ('id', 'user', 'params', 'request_for', 'use_count', 'created', 'modified')
	list_filter = ('created', 'modified')
	search_fields = ('id', 'user__username', 'params', 'request_for', 'use_count', 'created', 'modified')
	raw_id_fields = ('user',)
	readonly_fields = ('created', 'modified',)

	def get_queryset(self, request):
	    return super(SearchQueryAdmin, self).get_queryset(request).select_related('user').order_by('-id')


admin.site.register(SearchQuery, SearchQueryAdmin)

class ActionLogAdmin(admin.ModelAdmin):
	list_display = ('id', 'user', 'recipient_company', 'relationship_type', 'action_type', 'created')
	list_filter = ('created', )
	search_fields = ('id', 'user__username', 'recipient_company__name', 'relationship_type', 'action_type', 'created')
	raw_id_fields = ('user','recipient_company')

	def get_queryset(self, request):
	    return super(ActionLogAdmin, self).get_queryset(request).select_related('user','recipient_company').order_by('-id')


admin.site.register(ActionLog, ActionLogAdmin)

class AdvancedProfileAdmin(admin.ModelAdmin):
	list_display = ('id', 'company', 'est_year', 'shop_ownership', 'product_min_price', 'product_max_price')
	search_fields = ('id', 'company__name', 'est_year', 'shop_ownership', 'product_min_price', 'product_max_price')
	raw_id_fields = ('company',)

	def get_queryset(self, request):
	    return super(AdvancedProfileAdmin, self).get_queryset(request).select_related('company').order_by('-id')


admin.site.register(AdvancedProfile, AdvancedProfileAdmin)

class UserSavedFilterAdmin(admin.ModelAdmin):
	list_display = ('id', 'user', 'title', 'sub_text',)
	search_fields = ('id', 'user__username', 'title', 'sub_text',)
	raw_id_fields = ('user',)
	readonly_fields = ('created', 'modified',)

	def get_queryset(self, request):
	    return super(UserSavedFilterAdmin, self).get_queryset(request).select_related('user').order_by('-id')


admin.site.register(UserSavedFilter, UserSavedFilterAdmin)

class AppVersionAdmin(admin.ModelAdmin):
	list_display = ('id', 'version_code', 'update', 'force_update', 'platform')
	search_fields = ('id', 'version_code', 'update', 'force_update', 'platform')
	readonly_fields = ('created', 'modified',)

admin.site.register(AppVersion, AppVersionAdmin)

class DiscountRuleAdmin(admin.ModelAdmin):
	list_display = ('id', 'selling_compny', 'discount_type', 'all_brands', 'cash_discount', 'credit_discount', 'created', 'modified',)
	search_fields = ('id', 'selling_company__name', 'discount_type', 'all_brands', 'cash_discount', 'credit_discount')

	raw_id_fields = ('selling_company', 'brands', 'buyer_segmentations')
	readonly_fields = ('created', 'modified',)

	def get_queryset(self, request):
	    return super(DiscountRuleAdmin, self).get_queryset(request).select_related('selling_company')

	def selling_compny(self, obj):
		if obj.selling_company:
			return '<a href="%s" target="_blank">%s</a>' % ("/api/admin/api/company/"+str(obj.selling_company.id), obj.selling_company)
		return None
	selling_compny.allow_tags = True
	selling_compny.short_description = 'Selling Company'
	selling_compny.admin_order_field = 'selling_company_id'

admin.site.register(DiscountRule, DiscountRuleAdmin)

class CatalogEnquiryResource(resources.ModelResource):
    total_public_price = fields.Field()

    class Meta:
	    model = CatalogEnquiry
	    skip_unchanged = True
	    report_skipped = False
	    fields = ('id', 'catalog__title', 'total_public_price', 'selling_company__name', 'selling_company__phone_number','selling_company__city__city_name','selling_company__state__state_name', 'buying_company__name', 'buying_company__phone_number','buying_company__city__city_name','buying_company__state__state_name', 'status', 'created', 'enquiry_type', 'item_type', 'item_quantity', 'text')
	    export_order = ('id', 'catalog__title', 'total_public_price', 'selling_company__name', 'selling_company__phone_number','selling_company__city__city_name','selling_company__state__state_name', 'buying_company__name', 'buying_company__phone_number','buying_company__city__city_name','buying_company__state__state_name', 'status', 'created', 'enquiry_type', 'item_type', 'item_quantity', 'text')

    def get_queryset(self, request):
	    return super(CatalogEnquiry, self).get_queryset(request).select_related('catalog', 'selling_company', 'buying_company').prefetch_related('catalog__products')

    def dehydrate_total_public_price(self, obj):
	    try:
		price = 0
		products = obj.catalog.products.all()#.aggregate(Sum('public_price')).get('public_price__sum', 0)
		for product in products:
		    price += product.public_price

		return price
	    except:
		return ""

class CatalogEnquiryAdmin(ExportMixin, admin.ModelAdmin):
	list_display = ('id', 'catalog_detail', 'total_public_price', 'selling_compny', 'buying_compny', 'status', 'created', 'enquiry_type', 'item_type', 'item_quantity')
	search_fields = ('id', 'catalog__title', 'selling_company__name', 'buying_company__name', 'item_quantity')
	list_filter = ('status', 'enquiry_type', ('created', DateRangeFilter), 'item_type' )
	raw_id_fields = ('catalog', 'selling_company', 'buying_company')
	resource_class = CatalogEnquiryResource
	readonly_fields = ('created', 'modified',)

	def get_queryset(self, request):
	    return super(CatalogEnquiryAdmin, self).get_queryset(request).select_related('catalog', 'selling_company', 'buying_company').prefetch_related('catalog__products')

	def total_public_price(self, obj):
	    try:
		price = 0
		products = obj.catalog.products.all()#.aggregate(Sum('public_price')).get('public_price__sum', 0)
		for product in products:
		    price += product.public_price

		return price
	    except:
		return ""

	def catalog_detail(self, obj):
		if obj.catalog:
			return '<a href="%s" target="_blank">%s</a>' % ("/api/admin/api/catalog/"+str(obj.catalog.id), obj.catalog)
		return None
	catalog_detail.allow_tags = True
	catalog_detail.short_description = 'Catalog'
	catalog_detail.admin_order_field = 'catalogy_id'

	def selling_compny(self, obj):
		if obj.selling_company:
			return '<a href="%s" target="_blank">%s</a>' % ("/api/admin/api/company/"+str(obj.selling_company.id), obj.selling_company)
		return None
	selling_compny.allow_tags = True
	selling_compny.short_description = 'Selling Company'
	selling_compny.admin_order_field = 'selling_company_id'

	def buying_compny(self, obj):
		if obj.buying_company:
			return '<a href="%s" target="_blank">%s</a>' % ("/api/admin/api/company/"+str(obj.buying_company.id), obj.buying_company)
		return None
	buying_compny.allow_tags = True
	buying_compny.short_description = 'Buying Company'
	buying_compny.admin_order_field = 'buying_company__id'

admin.site.register(CatalogEnquiry, CatalogEnquiryAdmin)

class MarketingAdmin(admin.ModelAdmin):
	list_display = ('id', 'campaign_name', 'to', 'user', 'created')
	search_fields = ('id', 'campaign_name', 'to', 'user', 'created')
	raw_id_fields = ('user','test_users')
	filter_horizontal = ('state', 'city')
	readonly_fields = ('created', 'modified',)

	def get_queryset(self, request):
	    return super(MarketingAdmin, self).get_queryset(request).select_related('user')

admin.site.register(Marketing, MarketingAdmin)

class SellerPolicyAdmin(admin.ModelAdmin):
	list_display = ('id', 'company', 'policy_type')
	search_fields = ('id', 'company__name', 'policy_type')
	raw_id_fields = ('company',)
	readonly_fields = ('created', 'modified',)

	def get_queryset(self, request):
	    return super(SellerPolicyAdmin, self).get_queryset(request).select_related('company')

admin.site.register(SellerPolicy, SellerPolicyAdmin)


class MobileStateMappingResource(resources.ModelResource):
    class Meta:
	    model = MobileStateMapping
	    skip_unchanged = True
	    report_skipped = True
	    skip_row = True
	    fields = ('id', 'state', 'mobile_no_start_with', )
	    #exclude = ('id', )
	    import_id_fields = ('id', )
    def skip_row(self, instance, original):
        allfields = list(self.get_fields())

	#for field in allfields:
	#    print field.get_value(instance)

	allfields0 = allfields[0].get_value(instance)
	allfields1 = allfields[1].get_value(instance)
	allfields2 = allfields[2].get_value(instance)

	if MobileStateMapping.objects.filter(state=allfields1, mobile_no_start_with=allfields2).exists():
	    return True

        if not self._meta.skip_unchanged:
            return False
        for field in self.get_fields():
            try:
                # For fields that are models.fields.related.ManyRelatedManager
                # we need to compare the results
                if list(field.get_value(instance).all()) != list(field.get_value(original).all()):
                    return False
            except AttributeError:
                if field.get_value(instance) != field.get_value(original):
                    return False
        return True

class MobileStateMappingAdmin(ImportExportModelAdmin, admin.ModelAdmin):
	list_display = ('id', 'state', 'mobile_no_start_with', )
	#list_filter = ('id', 'company', )
	search_fields = ('id', 'state__state_name', 'mobile_no_start_with', )
	resource_class = MobileStateMappingResource

	def get_queryset(self, request):
	    return super(MobileStateMappingAdmin, self).get_queryset(request).select_related('state')

admin.site.register(MobileStateMapping, MobileStateMappingAdmin)


class UserCampaignClickResource(resources.ModelResource):
    person_name = fields.Field()
    phone_number = fields.Field()
    company = fields.Field()
    state = fields.Field()
    city = fields.Field()

    class Meta:
        model = UserCampaignClick
	fields = ('id', 'user__username', 'person_name', 'company', 'phone_number', 'state', 'city', 'campaign', 'created_at')
	export_order = ('id', 'user__username', 'person_name', 'company', 'phone_number', 'state', 'city', 'campaign', 'created_at')

    def get_queryset(self, request):
	    return super(UserCampaignClickResource, self).get_queryset(request).select_related('user__companyuser__company1')

    def dehydrate_person_name(self, obj):
	try:
		fullname = obj.user.first_name + " " + obj.user.last_name
		return fullname
	except:
		return ""

    def dehydrate_company(self, obj):
	try:
		global company
		company = None
		company = obj.user.companyuser.company
		return company.name
	except:
		return ""

    def dehydrate_phone_number(self, obj):
	try:
		return obj.user.userprofile.phone_number
	except:
		return ""

    def dehydrate_state(self, obj):
	    try:
		    global company
		    global address
		    address = None
		    try:
			address = company.address
		    except:
			address = obj.user.address_set.all()[0]
		    return address.state.state_name
	    except:
		    return ''

    def dehydrate_city(self, user):
	    try:
		    global company
		    global address
		    #company = user.companyuser.company
		    #return company.city.city_name
		    return address.city.city_name
	    except:
		    return ''

class UserCampaignClickAdmin(ExportMixin, admin.ModelAdmin):
	list_display = ('id', 'user', 'campaign', 'created_at')
	#list_filter = ('id', 'company', )
	search_fields = ('id', 'user__username', 'campaign', 'created_at')
	raw_id_fields = ('user', )
	resource_class = UserCampaignClickResource

	def get_queryset(self, request):
	    return super(UserCampaignClickAdmin, self).get_queryset(request).select_related('user')

admin.site.register(UserCampaignClick, UserCampaignClickAdmin)

class SalesOrderInternalAdmin(admin.ModelAdmin):
	list_display = ('id', 'salesorder', 'last_modified_by', 'internal_remark')
	#list_filter = ('id', 'company', )
	search_fields = ('id', 'salesorder__id', 'last_modified_by__username', 'internal_remark')
	raw_id_fields = ('salesorder', 'last_modified_by')

	def get_queryset(self, request):
	    return super(SalesOrderInternalAdmin, self).get_queryset(request).select_related('last_modified_by', 'salesorder')

admin.site.register(SalesOrderInternal, SalesOrderInternalAdmin)

class SellerStatisticResource(resources.ModelResource):
    class Meta:
        model = SellerStatistic


class SellerStatisticAdmin(ExportMixin, admin.ModelAdmin):
	list_display = ('id', 'company', 'name', 'company_type', 'city', 'phone_number', 'last_login', )
	#list_filter = ('id', 'company', )
	search_fields = ('id', 'company', 'name', 'company_type', 'city', 'phone_number', 'last_login', )
	raw_id_fields = ('company', )
	readonly_fields = ('created', 'modified',)

	def get_queryset(self, request):
	    return super(SellerStatisticAdmin, self).get_queryset(request).select_related('company')

admin.site.register(SellerStatistic, SellerStatisticAdmin)

class StoryAdmin(admin.ModelAdmin):
	list_display = ('id', 'name', 'is_disable', 'sort_order', 'created', 'modified',)
	list_filter = ('is_disable', )
	search_fields = ('id', 'name', 'is_disable', 'sort_order')
	raw_id_fields = ('catalogs', )
	readonly_fields = ('created', 'modified',)

	# ~ def get_queryset(self, request):
	    # ~ return super(StoryAdmin, self).get_queryset(request).select_related('catalogs')

admin.site.register(Story, StoryAdmin)

admin.site.register(ImageTest)


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 1
    show_change_link = True
    #form = SalesOrderItemInlineForm
    raw_id_fields = ('product', 'selling_company')

class CartAdmin(ExportMixin, admin.ModelAdmin):
	list_display = ('id', 'order_number', 'buying_company', 'person_name', 'order_type', 'total_amount', 'payment_method', 'created_type', 'cart_status', 'created', 'modified')
	list_filter = ('created_type', 'order_type', 'cart_status', ('created', DateRangeFilter), ('modified', DateRangeFilter) )
	search_fields = ('id', 'order_number', 'user__username', 'user__first_name', 'user__last_name', 'buying_company__name', 'buying_company__phone_number', 'ship_to__city__city_name', 'ship_to__state__state_name', 'order_type', 'total_amount', 'payment_method', 'created_type', 'created', 'modified')
	raw_id_fields = ('user', 'buying_company', 'broker_company', 'ship_to')
	readonly_fields = ('created', 'modified',)

	inlines = (CartItemInline, )

	def get_queryset(self, request):
	    return super(CartAdmin, self).get_queryset(request).select_related('user', 'buying_company', 'ship_to__city', 'ship_to__state').prefetch_related('items')

	def person_name(self, obj):
	    try:
			global userObj
			userObj = obj.user
			fullname = userObj.first_name + " " + userObj.last_name
			return fullname
	    except:
			return ""
	person_name.admin_order_field = 'user'

admin.site.register(Cart, CartAdmin)

class CartItemAdmin(ExportMixin, admin.ModelAdmin):
	list_display = ('id', 'order_number', 'product', 'quantity', 'rate', )
	list_filter = ('quantity', )
	search_fields = ('id', 'cart__order_number', 'product__title', 'quantity', 'rate',)
	raw_id_fields = ('cart', 'product',)

	def get_queryset(self, request):
	    return super(CartItemAdmin, self).get_queryset(request).select_related('cart', 'product')

	def order_number(self, obj):
	    try:
		order_number = obj.cart.order_number
		return order_number
	    except:
		return ""
	order_number.admin_order_field = 'cart__order_number'

admin.site.register(CartItem, CartItemAdmin)

class CompanyCreditAprovedLineAdmin(admin.ModelAdmin):
    list_display = ('id', 'company', 'nbfc_partner', 'approved_line', 'available_line', 'used_line')
    raw_id_fields = ('company',)
    list_filter = ('nbfc_partner',)
    search_fields = ('company__name', 'nbfc_partner', 'approved_line', 'available_line', 'used_line')
    readonly_fields = ('created', 'modified',)

admin.site.register(CompanyCreditAprovedLine, CompanyCreditAprovedLineAdmin)

class URLIndexAdmin(admin.ModelAdmin):
    list_display = ('id', 'urlobject_id', 'urltype', 'urlkey')
    #raw_id_fields = ('',)
    list_filter = ('urltype',)
    search_fields = ('urlobject_id', 'urltype', 'urlkey')

admin.site.register(URLIndex, URLIndexAdmin)

class CompanyBankDetailsAdmin(admin.ModelAdmin):
    list_display = ('id', 'company', 'bank_name', 'account_name', 'account_number', 'ifsc_code', 'account_type')
    raw_id_fields = ('company',)
    list_filter = ('account_type',)
    search_fields = ('company__name', 'bank_name', 'account_name', 'account_number', 'ifsc_code')
    readonly_fields = ('created', 'modified',)

admin.site.register(CompanyBankDetails, CompanyBankDetailsAdmin)

class CartPaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'mode', 'cart', 'amount', 'status', 'user', 'payment_details', 'created')
    raw_id_fields = ('cart','user',)
    list_filter = ('status','mode')
    search_fields = ('cart__order_number', 'amount', 'payment_details', 'user__username')
    readonly_fields = ('created', 'modified',)

admin.site.register(CartPayment, CartPaymentAdmin)
