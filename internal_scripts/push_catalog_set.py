from api.models import *

pushes = Push.objects.filter(shared_catalog__isnull=True).order_by('id')
print pushes

i = 0
for push in pushes:
	puObj = Push_User.objects.filter(push=push, catalog__isnull=False).first()
	if puObj:
		print "push id ="
		print push.id
		i += 1
		push.shared_catalog = puObj.catalog
		push.save()
		

print "tatal linked catalog = "
print i
