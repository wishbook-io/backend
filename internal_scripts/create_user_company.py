from api.models import *
from api.v0.serializers import *
from django.contrib.auth.models import User, Group

stateObj = State.objects.filter(state_name="gujarat").first()
cityObj = City.objects.filter(city_name="surat").first()
categoryObj = Category.objects.all().values_list('id', flat=True)
groupObj = Group.objects.get(name="administrator")

print "groupObj"
print groupObj

usr = CompanyUser.objects.all().values_list('user', flat=True)
userobj = User.objects.all().exclude(id__in=usr)
print "total users without company = "
print User.objects.all().exclude(id__in=usr).count()

for user in userobj:
    if not user.groups.filter(id = groupObj.id).exists():
        if user.groups.filter(name = "salesperson").exists() or user.groups.filter(name = "telecaller").exists():
            continue
        print "add group type to userid = "
        #user.groups.add(groupObj)
        #user.save()
    print user.id
    
    company = Company.objects.create(name=user.username, phone_number=user.userprofile.phone_number, city=cityObj, state=stateObj, country=user.userprofile.country, email=user.email)
    company.category.add(*categoryObj)
    company.save()
    
    companyType = CompanyType.objects.create(company=company)
    
    branch = Branch.objects.get_or_create(company = company, name="Main Branch - "+company.name, street_address=company.street_address, city=company.city, state=company.state, phone_number=company.phone_number, country=company.country)
    
    companyUser = CompanyUser.objects.create(user=user, company=company)
    
    city = City.objects.all().values_list('id', flat=True).distinct()
    category = Category.objects.all().values_list('id', flat=True).distinct()
    group_type = GroupType.objects.all().values_list('id', flat=True).distinct()
    
    buyerSegmentation = BuyerSegmentation.objects.create(segmentation_name="All Buyers",company=company)#city=city,category=category,
    buyerSegmentation.city = city #.add(city)
    buyerSegmentation.category = category #.add(category)
    buyerSegmentation.group_type = group_type
    
    
    buyerSegmentation = BuyerSegmentation.objects.create(segmentation_name="All Distributor",company=company)
    buyerSegmentation.city = city
    buyerSegmentation.category = category
    buyerSegmentation.group_type = GroupType.objects.filter(id=1).values_list('id', flat=True).distinct()
    
    buyerSegmentation = BuyerSegmentation.objects.create(segmentation_name="All Wholesaler",company=company)
    buyerSegmentation.city = city
    buyerSegmentation.category = category
    buyerSegmentation.group_type = GroupType.objects.filter(id=2).values_list('id', flat=True).distinct()
    
    buyerSegmentation = BuyerSegmentation.objects.create(segmentation_name="All Semi-Wholesaler",company=company)
    buyerSegmentation.city = city
    buyerSegmentation.category = category
    buyerSegmentation.group_type = GroupType.objects.filter(id=3).values_list('id', flat=True).distinct()
    
    buyerSegmentation = BuyerSegmentation.objects.create(segmentation_name="All Retailer",company=company)
    buyerSegmentation.city = city
    buyerSegmentation.category = category
    buyerSegmentation.group_type = GroupType.objects.filter(id=4).values_list('id', flat=True).distinct()
    
    buyerSegmentation = BuyerSegmentation.objects.create(segmentation_name="All Online-Retailer",company=company)
    buyerSegmentation.city = city
    buyerSegmentation.category = category
    buyerSegmentation.group_type = GroupType.objects.filter(id=5).values_list('id', flat=True).distinct()
    
    buyerSegmentation = BuyerSegmentation.objects.create(segmentation_name="All Resellers",company=company)
    buyerSegmentation.city = city
    buyerSegmentation.category = category
    buyerSegmentation.group_type = GroupType.objects.filter(id=8).values_list('id', flat=True).distinct()
    
    buyerSegmentation = BuyerSegmentation.objects.create(segmentation_name="All Broker",company=company)
    buyerSegmentation.city = city
    buyerSegmentation.category = category
    buyerSegmentation.group_type = GroupType.objects.filter(id=9).values_list('id', flat=True).distinct()
    ##end default segmentation
    
    warehouse = Warehouse.objects.create(company=company, name=company.name+" warehouse")
    
    makeBuyerSupplierFromInvitee(company.phone_number, company.country, company)

    

