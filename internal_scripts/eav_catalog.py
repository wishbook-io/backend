from api.models import *
from django.contrib.auth.models import User, Group

from eav.models import Attribute, Value as EavValue
from django.contrib.contenttypes.models import ContentType

#ct = ContentType.objects.get(id=25)


catalogs = Catalog.objects.filter(id__gte=5739).order_by('id')
#catalogs = Catalog.objects.filter(id__gte=1340).order_by('id')
#catalogs = Catalog.objects.all().order_by('id')
#catalogs = Catalog.objects.filter(id=244).order_by('id')

#from api.common_functions import *
#print getCatalogEAV( Catalog.objects.get(id=486), "allInJson")


for catalog in catalogs:
	print "catalog id=",catalog.id
	product = Product.objects.filter(catalog=catalog).order_by('id').last()
	#product = Product.objects.filter(catalog=catalog, id=1031).order_by('id').last()
	if product:
		print "product id=",product.id
		att = product.eav.get_values()
		print "product eav data =", att
		#arr = []
		other = ""
		for v in att:
			#arr.append([str(v.attribute.name), str(v.value)])
			logger.info("catalog create eav array key = %s ,value = %s"% (v.attribute.name, v.value))
			if isinstance(v.value, list):
				logger.info("in isinstance(v.value, list)")
				for subdata in v.value:
					enumValue = EnumValue.objects.filter(value=subdata).first()
					if enumValue:
						setattr( catalog.eav, v.attribute.name, enumValue)
						catalog.save()
			else:
				print v.value
				if str(v.value).lower() == "other":
					continue
				
				enumValue = EnumValue.objects.filter(value=v.value).first()
				if enumValue and v.attribute.name not in ["work_text","fabric_text"]:
					logger.info("in if enumValue")
					setattr( catalog.eav, v.attribute.name, enumValue)
					catalog.save()
				elif v.attribute.name in ["work_text","fabric_text"]:
					logger.info("in work_text fabric_text")
					tempvalue = v.value.replace('"','').replace('[','').replace(']','')
					if other == "":
						other = tempvalue
					else:
						other += ", "+tempvalue
					setattr( catalog.eav, "other", other)
					catalog.save()
				else:
					logger.info("in last setattr( catalog.eav, v.attribute.name, v.value)")
					#set text value
					setattr( catalog.eav, v.attribute.name, v.value)
					catalog.save()
		#return arr


