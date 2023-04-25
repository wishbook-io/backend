from api.models import *

catalogs = Catalog.objects.all().order_by('id')
for catalog in catalogs:
	print "catalog.id = ", catalog.id
	disableProductsIds = ProductStatus.objects.filter(product__catalog=catalog, status='Disable', company=catalog.company).values_list('product', flat=True)
	catalog.total_products_uploaded = catalog.products.all().exclude(id__in=disableProductsIds).count()
	print "catalog.total_products_uploaded = ", catalog.total_products_uploaded
	catalog.save()
