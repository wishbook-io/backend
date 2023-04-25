from api.models import *

todayDate = date.today()

catalogs = Catalog.objects.filter(view_permission="public").order_by('id')
for catalog in catalogs:
	print "catalog id=",catalog.id
	status="Enable"
	if catalog.supplier_disabled:
		status="Disable"
	
	expiry_date = catalog.expiry_date
	if catalog.expiry_date is None:
		expiry_date = todayDate + timedelta(days=catalog.company.default_catalog_lifetime)
	
	csobj, created = CatalogSeller.objects.get_or_create(catalog=catalog, selling_company=catalog.company, selling_type="Public", sell_full_catalog=catalog.sell_full_catalog, status=status, expiry_date=expiry_date)
	print csobj, created
	
