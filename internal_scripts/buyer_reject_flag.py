from api.models import *
from api.v1.serializers import *
from django.contrib.auth.models import User, Group

buyers = Buyer.objects.filter(supplier_approval=False, buyer_approval=False).order_by('id')

print "total buyer=",buyers.count()
print "total buyer ids=",list(buyers)


Buyer.objects.filter(supplier_approval=False, buyer_approval=False).update(buyer_approval=True)

