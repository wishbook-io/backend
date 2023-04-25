from api.models import *
#from api.v1.serializers import *
#from django.contrib.auth.models import User, Group
from datetime import datetime, date, time, timedelta


invitees = Invitee.objects.raw("SELECT `api_invitee`.`id`, `api_invite`.`company_id`, `api_invitee`.`country_id`, `api_invitee`.`invitee_number`, `api_invitee`.`invitation_type`, MIN(`api_invitee`.`id`) AS `min_id`, COUNT(`api_invitee`.`id`) AS `total_rows` FROM `api_invitee` LEFT OUTER JOIN `api_invite` ON ( `api_invitee`.`invite_id` = `api_invite`.`id` ) GROUP BY `api_invite`.`company_id`, `api_invitee`.`country_id`, `api_invitee`.`invitee_number`, `api_invitee`.`invitation_type` HAVING `total_rows` > 1")
print invitees
print invitees.query
i = 0
delete_invitee_ids = []

print "start for loop"
for invitee in invitees:
	#if 799 == invitee.id:
	i += 1
	print invitee.__dict__
	#inviteeobj = Invitee.objects.filter(invite__company=invitee.company_id, country=invitee.country, invitee_number=invitee.invitee_number).exclude(id=invitee.id)
	excludinviteeids = []
	inobj = Invitee.objects.filter(invite__company=invitee.company_id, country=invitee.country, invitee_number=invitee.invitee_number, invitation_type=invitee.invitation_type, invitee_id__status__in=["approved","rejected","supplier_pending","buyer_pending","Pending References","Transferred","References Filled"]).order_by('id').first()
	if inobj:
		excludinviteeids.append(inobj.id)
		print "exlude invitee id = ", excludinviteeids
	#inviteeobjs = Invitee.objects.filter(invite__company=invitee.company_id, country=invitee.country, invitee_number=invitee.invitee_number).exclude(Q(invitee_id__status__in=["approved","rejected","supplier_pending","buyer_pending","Pending References","Transferred","References Filled"]) | Q(invitee_id__isnull=True))
	inviteeobjs = Invitee.objects.filter(invite__company=invitee.company_id, country=invitee.country, invitee_number=invitee.invitee_number, invitation_type=invitee.invitation_type).exclude(id__in = excludinviteeids)
	
	#print inviteeobjs.values_list('invitee_id__status', flat=True)
	#print inviteeobjs.count()
	if inviteeobjs.count() == invitee.total_rows:
		inviteeobjs = inviteeobjs.exclude(id=invitee.id)
	#print inviteeobjs.values_list('invitee_id__status', flat=True)
	print "total_rows to delete before = ", invitee.total_rows
	print "total_rows to delete after = ", inviteeobjs.count()
	
	
	delete_invitee_ids.extend(inviteeobjs.values_list('id', flat=True))


print "i ==", i

print "delete_invitee_ids = "
print delete_invitee_ids
print "total delete_invitee_ids = ", len(delete_invitee_ids)

#inv = Invitee.objects.filter(id__in = delete_invitee_ids).delete()

