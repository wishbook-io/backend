from api.models import URLIndex

from api.models import Catalog

catalogs_qs = Catalog.objects.all().order_by('id')

for cata_obj in catalogs_qs:
	print "catalog id = ", cata_obj.id
	if not URLIndex.objects.filter(urlobject_id = cata_obj.id, urltype='Catalog').exists():
		urlkey_value = '-'.join(cata_obj.brand.name.split()) + '-' + '-'.join(cata_obj.title.split()) + '-' + str(cata_obj.id)
		urlkey_value = urlkey_value.lower()
		urlindex_obj = URLIndex(urlobject_id=cata_obj.id, urltype = 'Catalog', urlkey=urlkey_value)
		urlindex_obj.save()
