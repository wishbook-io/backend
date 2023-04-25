from api.models import *

addresses = Address.objects.filter(Q(location_city__isnull=False, location_state__isnull=False) & Q(Q(city__city_name="-") | Q(state__state_name="-"))).order_by('-id')

print "addresses len = ",addresses.count()

for address in addresses:
	print "address id=", address.id
	
	stateObj = State.objects.filter(state_name=address.location_state).first()
	if stateObj :
		address.state=stateObj

	cityObj = City.objects.filter(city_name=address.location_city).first()
	if cityObj :
		address.city=cityObj

	address.save()
	

print "addresses len = ",addresses.count()
