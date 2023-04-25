from django.forms import widgets
from rest_framework import serializers
from api.models import *
from django.contrib.auth.models import User, Group
from rest_framework import permissions
from django.conf import settings

from push_notifications.models import GCMDevice #,APNSDevice

import requests
from django.db.models import Sum
import datetime
      
from django.core.exceptions import ObjectDoesNotExist

import random

#from rest_framework.validators import UniqueTogetherValidator

def sendInvite(mobile_number, username):
	url = 'http://www.myvaluefirst.com/smpp/sendsms?username=<TOADD>&password=<TOADD>&to='+mobile_number+'&from=TRVENI&text=You%20are%20invited%20by%20'+username+'%20to%20use%20Wishbook%20App.%20Download%20Wishbook%20App%20from%20http%3A%2F%2Fwishbook.smedge.in%2Fwishbook.apk&dlr-mask=TRVENI'
	sendsmart= requests.get(url)
	
	print sendsmart
	
	return sendsmart

def sendOTP(mobile_number, otp):
	url = 'http://www.myvaluefirst.com/smpp/sendsms?username=<TOADD>&password=<TOADD>&to='+mobile_number+'&from=TRVENI&text=Dear%20Customer%2C%20One%20Time%20Password%20(OTP)%20to%20complete%20your%20online%20registration%20for%20Wishbook%20is%20'+otp+'.%20Do%20NOT%20share%20it%20with%20anyone&dlr-mask=TRVENI'
	sendsmart= requests.get(url)
	
	print sendsmart
	
	return sendsmart
		
class StateSerializer(serializers.ModelSerializer):
	class Meta:
		model = State
		
class CitySerializer(serializers.ModelSerializer):
	state_name = serializers.CharField(source='state.state_name', read_only=True)
	class Meta:
		model = City
	
class CompanyUserSerializer(serializers.ModelSerializer):
	username = serializers.CharField(source='user.username', read_only=True)
	companyname = serializers.CharField(source='company.name', read_only=True)
	class Meta:
		model = CompanyUser
		# fields = ('id', 'first_name', 'last_name', 'company', 'relationship_type', 'username')
		
class UserNumberSerializer(serializers.ModelSerializer):
	class Meta:
		model = UserNumber
		# fields = ('phone_number',)

class UserProfileSerializer(serializers.ModelSerializer):
	class Meta:
		model = UserProfile
		fields = ('alternate_email','phone_number', 'user_image')

class GetUserProfileSerializer(serializers.ModelSerializer):
	class Meta:
		model = UserProfile
		fields = ('id','user','alternate_email','phone_number', 'user_image', 'user_image_url')

class GroupSerializer(serializers.ModelSerializer):
	class Meta:
		model = Group
		fields = ('id', 'name')
			
class UserSerializer(serializers.ModelSerializer):
	#phone_nos = UserNumberSerializer(many=True, read_only=True)
	userprofile = UserProfileSerializer()
	companyuser = CompanyUserSerializer(read_only=True)
	companyid = serializers.CharField(required=False)
	#groups = GroupSerializer(many=True)
	#user_group = serializers.CharField(write_only=True)
	'''def __init__(self, *args, **kwargs):
		super(UserSerializer, self).__init__(*args, **kwargs)
		self.fields['username'].error_messages.update({
			'unique': 'Username is already taken'
		})'''
		
	class Meta:
		model = User
		fields = ('id', 'username', 'first_name', 'last_name', 'email', 'groups', 'companyuser', 'userprofile', 'password', 'companyid')# 'user_group',
		write_only_fields = ('password')
		'''error_messages = {
            'username': {
                'unique':'Username is already taken.',
            },
        }'''
	def update(self, instance, validated_data):
		userprofile_data = validated_data.pop('userprofile')
		
		print "before phone"
		phoneNumber = userprofile_data.get('phone_number', None)
		if phoneNumber is not None and UserProfile.objects.filter(phone_number=phoneNumber).exclude(user=instance.id).exists():
			print "IN phone"
			raise serializers.ValidationError("User is registered with this number")
		print "after phone"
		
		instance.username = validated_data.get('username', instance.username)
		instance.first_name = validated_data.get('first_name', instance.first_name)
		instance.last_name = validated_data.get('last_name', instance.last_name)
		instance.email = validated_data.get('email', instance.email)
		instance.groups = validated_data.get('groups', instance.groups)
		'''password = validated_data.get('password', instance.password)
		if password is not None:
			print "password="
			print password
			instance.set_password(password)'''
		instance.save()
		
		instance.userprofile.alternate_email = userprofile_data.get('alternate_email', instance.userprofile.alternate_email)
		#instance.userprofile.company_name = userprofile_data.get('company_name', instance.userprofile.company_name)
		instance.userprofile.phone_number = userprofile_data.get('phone_number', instance.userprofile.phone_number)
		instance.userprofile.save()
		
		return instance
	def create(self, validated_data):
		userprofile_data = validated_data.pop('userprofile')
		print "before phone"
		phoneNumber = userprofile_data.get('phone_number', None)
		if phoneNumber is not None and UserProfile.objects.filter(phone_number=phoneNumber).exists():
			raise serializers.ValidationError("User is registered with this number")
		print "after phone"
		user_group = validated_data.pop('groups')
		
		password = validated_data.pop('password')
		
		companyId = validated_data.pop('companyid', None)
		
		print "pass"
		usr = User.objects.create(**validated_data)
		usr.set_password(password)
		usr.groups = user_group#[users_group]
		usr.save()
		print "save"
		
		UserProfile.objects.filter(user=usr).update(**userprofile_data)
		
		if companyId is not None:
			companyUser = CompanyUser.objects.get_or_create(company=Company.objects.get(pk=companyId), user=usr)
			print companyUser

		return usr

class ChoiceSerializer(serializers.ModelSerializer):
	class Meta:
		model = Choice
		# fields = ('id', 'name', 'user', 'userlist')

class BranchSerializer(serializers.ModelSerializer):
	class Meta:
		model = Branch
		
class GetBranchSerializer(serializers.ModelSerializer):
	city = CitySerializer()
	state = StateSerializer()
	class Meta:
		model = Branch
		# fields = ()
		


class BrandSerializer(serializers.ModelSerializer):
	class Meta:
		model = Brand
		fields = ('id', 'name', 'company', 'image', 'image_url')

class BrandDistributorSerializer(serializers.ModelSerializer):
	class Meta:
		model = BrandDistributor

class CompanySerializer(serializers.ModelSerializer):
	admin = serializers.CharField(required=False)
	'''company_users = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
	branch_set = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
	def create(self, validated_data):
		company = Company.objects.create(**validated_data)
		return company'''
	class Meta:
		model = Company
		# fields = ('id', 'name', 'street_address', 'city', 'state', 'pincode', 'push_downstream')
	def create(self, validated_data):
		category = validated_data.get('category', None)
		if category is not None:
			category = validated_data.pop('category')
		else:
			category = Category.objects.all().values_list('id', flat=True)
		#sub_category = validated_data.pop('sub_category')
		adminId = validated_data.pop('admin', None)
		
		company = Company.objects.create(**validated_data)
		
		if adminId is not None:
			print "In Admin IF Cond."
			admin = User.objects.get(pk = adminId)
			groupObj = Group.objects.get(name="administrator")
			admin.groups.add(groupObj)
			admin.save()
			
			print CompanyUser.objects.filter(user = admin).exists()
			if CompanyUser.objects.filter(user = admin).exists():
				print "comp. user. if"
				adminCompany = CompanyUser.objects.filter(user = admin).update(company = company)
				print adminCompany
				#adminCompany.company = company
				#adminCompany.save()
			else:
				print "comp. user. else"
				CompanyUser.objects.create(user = admin, company = company)
		
		
		company.category = category
		#company.admin = admin
		
		#set Main branch
		branch = Branch.objects.get_or_create(company = company, name="Main Branch - "+company.name, street_address=company.street_address, city=company.city, state=company.state, phone_number=company.phone_number)# ,
		print branch
		
		sendInvite(str(company.phone_number), str(self.context['request'].user.username))
		
		return company

class GetCompanySerializer(serializers.ModelSerializer):
	###company_users = CompanyUserSerializer(many=True, read_only=True)
	###branch_set = BranchSerializer(many=True, read_only=True)
	###brand_set = BrandSerializer(many=True, read_only=True)
	#thumbnail_url = serializers.SerializerMethodField('get_image')
	#admin = UserSerializer(many=True)
	class Meta:
		model = Company
		depth = 1
	'''def get_image(self, obj):
		return '%s%s' % (settings.STATIC_URL, obj.thumbnail)'''






class BuyerSerializer(serializers.ModelSerializer):
	'''buying_company_name = serializers.CharField(source='buying_company.name', read_only=True)
	buying_company_street_address = serializers.CharField(source='buying_company.street_address', read_only=True)
	buying_company_city = serializers.CharField(source='buying_company.city', read_only=True)
	buying_company_phone = serializers.CharField(source='buying_company.phone_number', read_only=True)'''
	selling_company = serializers.ReadOnlyField(source='selling_company.name', read_only=True)#add user on create
	class Meta:
		model = Buyer
		# fields = ('id', 'buying_company', 'buying_company_name', 'buying_company_street_address', 'buying_company_city')
		'''validators = UniqueTogetherValidator(
            queryset=Buyer.objects.all(),
            fields=['selling_company', 'buying_company']
        )'''

class GetBuyerSerializer(serializers.ModelSerializer):
	buying_company = GetCompanySerializer()
	class Meta:
		model = Buyer
		fields = ('id', 'buying_company', 'status', 'fix_amount', 'percentage_amount')
		depth = 2

class SellerSerializer(serializers.ModelSerializer):
	buying_company = serializers.ReadOnlyField(source='buying_company.name', read_only=True)#add user on create
	class Meta:
		model = Buyer
		# fields = ('id', 'buying_company', 'buying_company_name', 'buying_company_street_address', 'buying_company_city')
		
class GetSellerSerializer(serializers.ModelSerializer):
	selling_company = GetCompanySerializer()
	class Meta:
		model = Buyer
		fields = ('id', 'selling_company', 'status', 'fix_amount', 'percentage_amount')
		depth = 2

class SalesOrderItemSerializer(serializers.ModelSerializer):
	product_title = serializers.CharField(source='product.title', read_only=True)
	class Meta:
		model = SalesOrderItem
		# fields = ('id', 'product', 'name', 'qty', 'rate')

class MeetingSerializer(serializers.ModelSerializer):
	buying_company = serializers.CharField(source='salesorder.company.id', read_only=True)
	user = serializers.ReadOnlyField(source='user.username', read_only=True)#add user on create
	duration = serializers.CharField(read_only=True)
	class Meta:
		model = Meeting
		readonly_fields = ("duration",)
		#fields = ('id', 'salesorder', 'buying_company', 'status')
		
class SalesOrderSerializer(serializers.ModelSerializer):
#	items = serializers.SlugRelatedField(slug_field='product',many=True, read_only=True)
	items = SalesOrderItemSerializer(many=True)
	###meeting = MeetingSerializer(many=True, read_only=True)#serializers.PrimaryKeyRelatedField(read_only=True)
	company_name = serializers.CharField(source='company.name', read_only=True)
	user = serializers.ReadOnlyField(source='user.username', read_only=True)
	seller_company = serializers.ReadOnlyField(source='seller_company.name', read_only=True)

	def create(self, validated_data):
		#catalog_id = validated_data.get('catalog')

		items = validated_data.pop('items')
		
		#salesorder = SalesOrder.objects.create(order_number=validated_data['order_number'], company=validated_data['company'],user=validated_data['user'])
		####salesorder = SalesOrder.objects.create(**validated_data)
		# Create or update each page instance
		
		'''product_catalog = Product.objects.filter(catalog__id = catalog_id)
		for item in product_catalog:
			salesitem = SalesOrderItem.objects.get_or_create(product=item, quantity=1, rate=item.price, sales_order = salesorder)'''
		
		
		companyGroup = []
		productGroup = []
		for item in items:
			companyId = item['product'].catalog.all()[0].company.id #Need catalog for company
			if companyId in companyGroup:
				productGroup[companyGroup.index(companyId)].append(item)
			else:
				companyGroup.append(companyId)
				temp = []
				temp.append(item)
				productGroup.append(temp)
			
		for index, companyId in enumerate(companyGroup):
			validated_data['seller_company'] = Company.objects.get(pk=companyId)
			salesorder = SalesOrder.objects.create(**validated_data)
			#salesorder.save(seller_company=Company.objects.get(pk=companyId))
			###salesorder = SalesOrder.objects.create(order_number=validated_data['order_number'], company=validated_data['company'], seller_company=Company.objects.get(pk=companyId), user=self.context['request'].user)
			
			items = productGroup[index]
			
			for item in items:
				
				salesitem = SalesOrderItem.objects.get_or_create(product=item['product'], quantity=item['quantity'], rate=item['rate'],sales_order = salesorder)
		 
		
		
		'''for item in items:
			salesitem = SalesOrderItem.objects.get_or_create(product=item['product'], quantity=item['quantity'], rate=item['rate'],sales_order = salesorder)
		'''
		
		return salesorder
		
	'''def update(self, instance, validated_data):
		instance.processing_status = validated_data.get('processing_status', instance.processing_status)
		instance.customer_status = validated_data.get('customer_status', instance.customer_status)
		instance.save()
		return instance'''
			
	class Meta:
		model = SalesOrder
		fields = ('id', 'order_number', 'company', 'total_rate', 'date', 'time', 'processing_status', 'customer_status', 'user','items','screenshot', 'company_name', 'seller_company', 'note', 'total_products')
		#write_only_fields = ('order_number', 'company', 'user', 'items')
	


class ChannelTypeSerializer(serializers.ModelSerializer):
	class Meta:
		model = ChannelType
		# fields = ('id', 'name', 'credential_format', 'file_format')

class ChannelSerializer(serializers.ModelSerializer):
	class Meta:
		model = Channel
		# fields = ('id', 'channel_type', 'name')
		
'''		
class PushResultSerializer(serializers.ModelSerializer):
	class Meta:
		model = Push_Result
		fields = ('id', 'push', 'num_people_targeted', 'num_app_users', 'num_product_views')
'''
class PushCatalogSerializer(serializers.ModelSerializer):
	class Meta:
		model = Push_Catalog
		fields = ('id', 'push', 'catalog')
		
class PushSelectionSerializer(serializers.ModelSerializer):
	class Meta:
		model = Push_Selection
		fields = ('id', 'push', 'selection')
		
class PushSerializer(serializers.ModelSerializer):
	user = serializers.ReadOnlyField(source='user.username', read_only=True)
	#push_users = PushUserSerializer(many=True, required=False)
	push_catalog = PushCatalogSerializer(many=True)
	push_selection = PushSelectionSerializer(many=True)
	#push_result = PushResultSerializer(many=True, required=False)
	company = serializers.ReadOnlyField(source='company.name', read_only=True)#add user on create
	
	def create(self, validated_data):
		#push_users = validated_data.pop('push_users')
		push_catalog = validated_data.pop('push_catalog')
		push_selection = validated_data.pop('push_selection')
		
		message = validated_data.get('message', '')
		
		pushobj = Push.objects.create(**validated_data)
		
		#for item in push_result:
		##pushresult = Push_Result.objects.get_or_create(push=pushobj)
		title = ''
		pushImage = ''
		pushType = ''
		#for add catalog in push
		if push_catalog:
			for item in push_catalog:
				pushcatalog = Push_Catalog.objects.get_or_create(push=pushobj, catalog=item['catalog'])
				title = item['catalog'].title+" - "+message
				pushImage = item['catalog'].thumbnail_url()
				pushType="catalog"
			
		#for add selection in push
		if push_selection:
			for item in push_selection:
				pushselection = Push_Selection.objects.get_or_create(push=pushobj, selection=item['selection'])
				title = item['selection'].name+" - "+message
				pushImage = item['selection'].products.all()[0].image_small_url()
				pushType="selection"
		#for add push user 
		print title
		
		city = pushobj.buyer_segmentation.city.all().values_list('id', flat=True)
		category = pushobj.buyer_segmentation.category.all().values_list('id', flat=True)
		print "==city=="
		print city
		print "==category=="
		print category

		companyIds = Branch.objects.filter(Q(city__in=city)).values_list('company', flat=True)
		print "==current user=="
		print self.context['request'].user.companyuser.company.push_downstream
		
		push_downstream = self.context['request'].user.companyuser.company.push_downstream
		
		print "==company=="
		print pushobj.buyer_segmentation.company
		
		buyerIds = Buyer.objects.filter(selling_company = pushobj.buyer_segmentation.company).values_list('buying_company', flat=True).distinct()
		#idLoop = 
		#idLoop = buyerIds
		'''print buyerIds
		print idLoop
		print len(buyerIds)
		print push_downstream
		if push_downstream=='yes':
			
			#print idLoop
			#print len(idLoop)
			while len(idloop)>0:
				print "================"
				downstreamBuyerIds = Buyer.objects.filter(selling_company__in = idloop).values_list('buying_company', flat=True).distinct()
				print downstreamBuyerIds
				downstreamBuyerIds = downstreamBuyerIds.remove(buyerIds)
				print downstreamBuyerIds
				idLoop = downstreamBuyerIds
				buyerIds = set(buyerIds+downstreamBuyerIds)
				print buyerIds
		'''
		
		print "==All companyIds=="
		print companyIds
		print "==My buyerIds=="
		print buyerIds
		buyerCompanyIds = list(set(companyIds).intersection(buyerIds))
		print "==Filtered city wise buyerCompanyIds=="
		print buyerCompanyIds

		companyCategoryIds = Company.objects.filter(id__in=buyerCompanyIds, category__in=category).order_by('id').values_list('id', flat=True).distinct()
		allCompanyUser = CompanyUser.objects.filter(company__in=companyCategoryIds, user__groups__name="administrator").values_list('user', flat=True).distinct() #.exclude(user=self.context['request'].user).order_by('user')
		print "==Filtered category wise companyCategoryIds=="
		print companyCategoryIds
		print "==push administrator-user list=="
		print allCompanyUser
		for userid in allCompanyUser:
			try:
				pushuser = Push_User.objects.get_or_create(push=pushobj, user=User.objects.get(pk=userid))
			except ObjectDoesNotExist:
				pushuser = None

		device = GCMDevice.objects.filter(user__in=allCompanyUser)#.latest("date_created")
		# The first argument will be sent as "message" to the intent extras Bundle
		# Retrieve it with intent.getExtras().getString("message")
		#status = device.send_message({'from':2, 'message':'okoko'})
		
		print device
		
		status = device.send_message(title, extra={"push_id": pushobj.id,"notId":pushobj.id,"push_type":pushType,"image":pushImage})#pushobj.push_type

		print status

		return pushobj
	
	class Meta:
		model = Push
		#depth = 1
		fields = ('id', 'date', 'time', 'push_type', 'push_downstream', 'status', 'message', 'buyer_segmentation', 'company', 'push_catalog', 'push_selection', 'user')

class GetPushSerializer(serializers.ModelSerializer):	
	#push_users = PushUserSerializer(many=True, required=False)
	push_catalog = PushCatalogSerializer(many=True)
	push_selection = PushSelectionSerializer(many=True)
	buyer_segmentation_name = serializers.CharField(source='buyer_segmentation.segmentation_name', read_only=True)

	class Meta:
		model = Push
		#depth = 1
		fields = ('id', 'date', 'time', 'push_type', 'push_downstream', 'status', 'message', 'buyer_segmentation', 'buyer_segmentation_name', 'company', 'push_catalog', 'push_selection', 'total_users', 'total_viewed', 'total_products', 'push_amount', 'user')

class PushUserSerializer(serializers.ModelSerializer):
	push = PushSerializer()
	class Meta:
		model = Push_User
		fields = ('id', 'push', 'user', 'is_viewed')
		
class PushProductSerializer(serializers.ModelSerializer):
	class Meta:
		model = Push_Product
		fields = ('id', 'push', 'product')
		
class ProductSerializer(serializers.ModelSerializer):
	#catalog_title = serializers.CharField(source='catalog.title', read_only=True)
	#push_product_id = PushProductSerializer(many=True, read_only=True, required=False)

	'''catalog = serializers.CharField(write_only=True, required=False)
	def create(self, validated_data):
		catalog = validated_data.pop('catalog')
		print catalog

		product = Product.objects.create(**validated_data)
		print product
		
		#product.catalog = catalog#[users_group
		catalogs = catalog.split(',')
		for catalog in catalogs:
				catalogObj = Catalog.objects.get(pk=catalog)
				product.catalog.add(catalogObj)

		return product'''
		
	class Meta:
		model = Product
		fields = ('id', 'sku', 'title', 'fabric', 'price', 'work', 'catalog', 'image_small')
		#write_only_fields = ('catalog')
'''
class UpdateProductSerializer(serializers.ModelSerializer):

	class Meta:
		model = Product
		fields = ('id', 'sku', 'title', 'fabric', 'price', 'work', 'catalog', 'image_small')
'''	
class GetProductSerializer(serializers.ModelSerializer):
	#catalog_title = serializers.CharField(source='catalog.title', read_only=True)
	###push_product_id = PushProductSerializer(many=True, read_only=True, required=False)
	#image_small_url = serializers.SerializerMethodField('get_small')
	'''image_small = serializers.ImageField(
        max_length=None, use_url=False,
    )'''

	class Meta:
		model = Product
		fields = ('id', 'sku', 'title', 'fabric', 'price', 'work', 'catalog', 'image_small','image_small_url')
		depth = 1

	'''def get_small(self, obj):
		return '%s%s' % (settings.STATIC_URL, obj.image_small)'''


class GetSelectionSerializer(serializers.ModelSerializer):
	thumbnail_url = serializers.SerializerMethodField('get_image')
	user = serializers.ReadOnlyField(source='user.username', read_only=True)
	products = GetProductSerializer(many=True)
	class Meta:
		model = Selection
		depth = 1
	def get_image(self, obj):
		return '%s%s' % (settings.STATIC_URL, obj.thumbnail)

class SelectionSerializer(serializers.ModelSerializer):
	# user = serializers.HiddenField(default=serializers.CurrentUserDefault())
	user = serializers.ReadOnlyField(source='user.username', read_only=True)#add user on create
	class Meta:
		model = Selection
		fields = ('id', 'user', 'name', 'products', 'thumbnail')
		#depth = 1
		
				
class CatalogSerializer(serializers.ModelSerializer):
	###push_catalog_id = PushCatalogSerializer(many=True, required=False, read_only=True)
	###products = ProductSerializer(many=True, required=False, read_only=True)
	company = serializers.ReadOnlyField(source='company.name', read_only=True)
	picasa_url = serializers.ReadOnlyField(read_only=True)
	picasa_id = serializers.ReadOnlyField(read_only=True)
	class Meta:
		model = Catalog
		fields = ('id', 'brand', 'title', 'thumbnail', 'view_permission', 'category', 'company', 'picasa_url', 'picasa_id', 'total_products')
		
class GetCatalogSerializer(serializers.ModelSerializer):
	###push_catalog_id = PushCatalogSerializer(many=True, required=False, read_only=True)
	brand = BrandSerializer()
	products = GetProductSerializer(many=True, required=False, read_only=True)
	#thumbnail_url = serializers.SerializerMethodField('get_image')
	class Meta:
		model = Catalog
		fields = ('id', 'brand', 'title', 'thumbnail', 'thumbnail_url', 'view_permission', 'category', 'products', 'company', 'picasa_url', 'picasa_id', 'total_products')
		depth = 1
	'''def get_image(self, obj):
		return '%s%s' % (settings.STATIC_URL, obj.thumbnail)'''
		
class ExportSerializer(serializers.ModelSerializer):
	class Meta:
		model = Export
		fields = ('id', 'channel', 'date', 'time')

class ExportResultSerializer(serializers.ModelSerializer):
	class Meta:
		model = Export_Result
		fields = ('id', 'export', 'file_path')

class ExportCatalogSerializer(serializers.ModelSerializer):
	class Meta:
		model = Export_Catalog
		fields = ('id', 'export', 'catalog')

class ExportProductSerializer(serializers.ModelSerializer):
	class Meta:
		model = Export_Product
		fields = ('id', 'export', 'product')

class InviteSerializer(serializers.ModelSerializer):
	user = serializers.ReadOnlyField(source='user.username', read_only=True)#add user on create
	company = serializers.ReadOnlyField(source='company.name', read_only=True)#add user on create
	class Meta:
		model = Invite
		# fields = ('id', 'company', 'relationship_type', 'date', 'time', 'user')
		
class GetInviteSerializer(serializers.ModelSerializer):
	class Meta:
		model = Invite

class InviteeSerializer(serializers.ModelSerializer):
	relationship_type = serializers.CharField(source='invite.relationship_type', read_only=True)
	def create(self, validated_data):
		inviteeNumber = validated_data.get('invitee_number', None)
		if UserProfile.objects.filter(phone_number=inviteeNumber).exists():
			raise serializers.ValidationError("User is registered with this number")
		
		invitee = Invitee.objects.create(**validated_data)
		
		sendInvite(str(invitee.invitee_number), str(self.context['request'].user.username))
		
		return invitee
		
	'''def update(self, instance, validated_data):
		sendInvite(str(instance.invitee_number), str(instance.id))
		
		instance.save()
		return instance'''
		
	class Meta:
		model = Invitee
		# fields = ('id', 'invite', 'invitee_number', 'invitee_company', 'invitee_name', 'is_converted')

class MessageSerializer(serializers.ModelSerializer):
	sender_username = serializers.CharField(source='sender_user.username', read_only=True)
	class Meta:
		model = Message
		# fields = ('id', 'datetime', 'sender_user', 'receiver_user', 'subject', 'mtype', 'body')

class ReceivedMessageSerializer(serializers.ModelSerializer):
	receiver_user = serializers.HiddenField(default=serializers.CurrentUserDefault())
	class Meta:
		model = Message
		# fields = ('id', 'datetime', 'sender_user', 'receiver_user', 'subject', 'mtype', 'body')

class SentMessageSerializer(serializers.ModelSerializer):
	sender_user = serializers.HiddenField(default=serializers.CurrentUserDefault())
	class Meta:
		model = Message
		fields = ('id', 'datetime', 'sender_user', 'receiver_user', 'subject', 'mtype', 'body')

class MessageFolderSerializer(serializers.ModelSerializer):
	class Meta:
		model = MessageFolder
		# fields = ('id', 'message', 'folder', 'status')


class BuyerSegmentationSerializer(serializers.ModelSerializer):
	###push_buyer_segmentation = PushSerializer(many=True, required=False, read_only=True)
	company = serializers.ReadOnlyField(source='company.name', read_only=True)
	#phone_nos = serializers.SlugRelatedField(read_only=True, many=True, slug_field='phone_number')
	#city_nam = serializers.CharField(source='city.city_name', read_only=True, many=True)
	#city_nam = serializers.SlugRelatedField(read_only=True, many=True, slug_field='city_name')
	class Meta:
		model = BuyerSegmentation
		fields = ('id', 'segmentation_name', 'city', 'category', 'active_buyers', 'last_generated', 'company')

class GetBuyerSegmentationSerializer(serializers.ModelSerializer):
	###push_buyer_segmentation = PushSerializer(many=True, required=False, read_only=True)
	class Meta:
		model = BuyerSegmentation
		fields = ('id', 'segmentation_name', 'city', 'category', 'active_buyers', 'last_generated')#, 'company'
		depth = 1
		


class Child3CategorySerializer(serializers.ModelSerializer):
	class Meta:
		model = Category	
		
class Child2CategorySerializer(serializers.ModelSerializer):
	child_category = Child3CategorySerializer(many=True, required=False, read_only=True)
	class Meta:
		model = Category
		
class Child1CategorySerializer(serializers.ModelSerializer):
	child_category = Child2CategorySerializer(many=True, required=False, read_only=True)
	class Meta:
		model = Category
		
class CategorySerializer(serializers.ModelSerializer):
	child_category = Child1CategorySerializer(many=True, required=False, read_only=True)
	class Meta:
		model = Category
'''		
class MainCategorySerializer(serializers.ModelSerializer):
	class Meta:
		model = MainCategory
		
class SubCategorySerializer(serializers.ModelSerializer):
	class Meta:
		model = SubCategory
'''
class InvoiceSerializer(serializers.ModelSerializer):
	def create(self, validated_data):
		invoice = Invoice.objects.create(**validated_data)
		
		push_ids = Push.objects.filter(company=invoice.company, date__gte=invoice.start_date, date__lte=invoice.end_date).values_list('id', flat=True)#,company=invoice.company
		print "ids=="
		print push_ids
		invoice.push = push_ids
		print invoice.push
		
		pushList = Push.objects.filter(id__in=push_ids)
		total_push_amount = 0
		for pushObj in pushList:
			total_push_amount += pushObj.push_amount()

		invoice.charges_amount = total_push_amount
		
		# HOW to compaire Expire DaTE
		invoice_credit = InvoiceCredit.objects.filter(expire_date__gte=invoice.end_date, company=invoice.company).aggregate(Sum('credit_amount')).get('credit_amount__sum', 0)#datetime.date.today()
		invoice_credit_ids = InvoiceCredit.objects.filter(expire_date__gte=invoice.end_date, company=invoice.company).values_list('id', flat=True)#datetime.date.today()
		
		print invoice_credit
		print invoice_credit_ids
		
		if invoice_credit is None:
			print "Is None"
			invoice_credit = 0
			
		total_charge = invoice.charges_amount
		
		if total_charge<invoice_credit:
			print "if"
			invoice.credit_amount = total_charge
			invoice.net_value = 0
			invoice.payment_status = 'paid'
			invoice.payment_datetime = datetime.datetime.now()
			#print datetime.datetime.now()
			for invoice_id in invoice_credit_ids:
				current_credit_invoice = InvoiceCredit.objects.get(pk=invoice_id)
				if current_credit_invoice.credit_amount > total_charge:
					current_credit_invoice.credit_amount -= total_charge
					current_credit_invoice.save()
					break
				else:
					total_charge -= current_credit_invoice.credit_amount
					current_credit_invoice.credit_amount = 0
					current_credit_invoice.save()
		
		elif total_charge>invoice_credit:
			print "elif"
			invoice.credit_amount = invoice_credit
			invoice.net_value = total_charge-invoice_credit
			for invoice_id in invoice_credit_ids:
				current_credit_invoice = InvoiceCredit.objects.get(pk=invoice_id)
				current_credit_invoice.credit_amount = 0
				current_credit_invoice.save()
		
		else:
			print "else"
			invoice.credit_amount = total_charge
			invoice.net_value = 0
			invoice.payment_status = 'paid'
			invoice.payment_datetime = datetime.datetime.now()
			for invoice_id in invoice_credit_ids:
				current_credit_invoice = InvoiceCredit.objects.get(pk=invoice_id)
				current_credit_invoice.credit_amount = 0
				current_credit_invoice.save()
				
		###
		invoice.save()

		return invoice
		
	class Meta:
		model = Invoice
		fields = ('id', 'company', 'payment_status', 'start_date', 'end_date')
		
class GetInvoiceSerializer(serializers.ModelSerializer):
	class Meta:
		model = Invoice
		#fields = ('id', 'company', 'status', 'start_date', 'end_date')

class InvoiceCreditSerializer(serializers.ModelSerializer):
	class Meta:
		model = InvoiceCredit

class RegistrationOTPSerializer(serializers.ModelSerializer):
	#otp = serializers.ReadOnlyField(read_only=True)
	#username = Field()
	def create(self, validated_data):
		phoneNumber = validated_data.get('phone_number', None)
		if UserProfile.objects.filter(phone_number=phoneNumber).exists():
			raise serializers.ValidationError("User is registered with this number")
		
		#username = validated_data.get('username', None)
		#print username
		
		otp = random.randrange(100000, 999999, 1)
		print phoneNumber
		sendOTP(str(phoneNumber), str(otp))
		
		registrationOtp = RegistrationOTP.objects.create(phone_number=phoneNumber, otp=otp)
		
		return registrationOtp
		
	class Meta:
		model = RegistrationOTP
		fields = ('phone_number', 'created_date')

class GetRegistrationOTPSerializer(serializers.ModelSerializer):
	class Meta:
		model = RegistrationOTP
		fields = ('id', 'phone_number', 'created_date', 'otp')
