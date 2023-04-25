from api.models import *
import eav
from eav.models import *

#EnumGroup.objects.filter(name='fabric', enums__value='silk')
#EnumValue.objects.all()

categoryObjs = Category.objects.all()
attributeObjs = Attribute.objects.all()

for category in categoryObjs:
	for attribute in attributeObjs:
		print category
		print attribute
		CategoryEavAttribute.objects.get_or_create(category=category, attribute=attribute)

productObjs = Product.objects.all()
eav.register(Product)

for product in productObjs:
	if product.fabric is not None and product.fabric != "":
		if not EnumGroup.objects.filter(name='fabric', enums__value=product.fabric).exists():
			if not EnumValue.objects.filter(value=product.fabric).exists():
				EnumValue.objects.create(value=product.fabric)
			enumGroupObj = EnumGroup.objects.get(name='fabric')
			enumValueObj = EnumValue.objects.get(value=product.fabric)
			enumGroupObj.enums.add(enumValueObj)
		
		product.eav.fabric = EnumValue.objects.get(value=product.fabric)
		product.eav.fabric_text = product.fabric
	
	if product.work is not None and product.work != "":
		if not EnumGroup.objects.filter(name='work', enums__value=product.work).exists():
			if not EnumValue.objects.filter(value=product.work).exists():
				EnumValue.objects.create(value=product.work)
			enumGroupObj = EnumGroup.objects.get(name='work')
			enumValueObj = EnumValue.objects.get(value=product.work)
			enumGroupObj.enums.add(enumValueObj)
		
		product.eav.work = EnumValue.objects.get(value=product.work)
		product.eav.work_text = product.work
	
	'''if EnumGroup.objects.filter(name='fabric', enums__value=product.fabric).exists():
		print "EnumGroup"
		eg = EnumGroup.objects.filter(name='fabric', enums__value=product.fabric).first()
		product.eav.fabric = eg.enums.filter(value=product.fabric).first()
	else:
		product.eav.fabric_text = product.fabric
	
	if EnumGroup.objects.filter(name='work', enums__value=product.work).exists():
		print "EnumGroup"
		eg = EnumGroup.objects.filter(name='work', enums__value=product.work).first()
		product.eav.work = eg.enums.filter(value=product.work).first()
	else:
		product.eav.work_text = product.work'''
	print product.eav
	product.save()
