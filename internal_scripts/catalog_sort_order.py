from api.models import *

catalogs = Catalog.objects.filter(sort_order=0).order_by('id')
for catalog in catalogs:
	print catalog.id
	catalog.sort_order = catalog.id
	catalog.save()


