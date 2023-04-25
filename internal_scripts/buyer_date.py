from api.models import *
from django.contrib.auth.models import User, Group

buyerObjs = Buyer.objects.filter(invitee__isnull=False).select_related('invitee__invite').order_by('id')
print "before for loop"
for buyerObj in buyerObjs:
	try:
		print buyerObj.id
		buyerObj.created_at = buyerObj.invitee.invite.date
		buyerObj.save()
	except Exception as e:
		logger.info("In Exception")
		logger.info(str(e))
		pass
print "after for loop"
