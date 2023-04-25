from api.models import *
#from api.v1.serializers import *
from django.contrib.auth.models import User, Group

cids = []
for i in [0]:
	ids = Company.objects.filter(phone_number__startswith=i).values_list('id', flat=True)
	cids.extend(list(ids))

uids = []
for i in [0]:
	ids = UserProfile.objects.filter(phone_number__startswith=i).exclude(user__is_staff=True).values_list('user', flat=True)
	uids.extend(list(ids))

print "cids company ="
print cids

print "uids user ="
print uids

print "tatal company ="
print len(cids)

print "tatal user ="
print len(uids)

'''c = Company.objects.filter(id__in=cids)
print c

u = User.objects.filter(id__in=uids)
print u'''

