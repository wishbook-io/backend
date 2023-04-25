from rest_framework import fields, serializers
from .notification_models import *



class NotificationSerializer(serializers.ModelSerializer):
	# state_name = serializers.CharField(source='state.state_name', read_only=True)

	class Meta:
		model = Notification
    	# fields = '__all__'


class NotificationEntitySerializer(serializers.ModelSerializer):
	# state_name = serializers.CharField(source='state.state_name', read_only=True)
	class Meta:
		model = NotificationEntity
    	# fields = '__all__'


class NotificationEntityTypeSerializer(serializers.ModelSerializer):
	#state_name = serializers.CharField(source='state.state_name', read_only=True)

	class Meta:
		model = NotificationEntityTemplate
    	# fields = '__all__'
