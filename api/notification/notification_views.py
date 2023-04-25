from rest_framework.decorators import api_view,permission_classes
from rest_framework import permissions, viewsets
from api.permissions import IsAdminOrReadOnly
from .notification_serializer import *

@api_view(["GET"])
@permission_classes((permissions.IsAdminUser,))
def catalog_notification(request):
    catalog_ids  = request.GET.get("catalog_id")
    notifier_ids = request.GET.getlist("notifier_ids")
    extra_ids    = request.GET.getlist("extra_ids")

class NotificationViewSet(viewsets.ModelViewSet):
    """
    Handles Notification request that comes from frontend.
    """
    queryset            = Notification.objects.all()
    serializer_class    = NotificationSerializer
    permission_classes  = (IsAdminOrReadOnly, )


class NotificationEntityViewSet(viewsets.ModelViewSet):
    """
    """
    queryset            = NotificationEntity.objects.all()
    serializer_class    = NotificationEntitySerializer
    permission_classes  = (IsAdminOrReadOnly, )


class NotificationEntityTypeViewSet(viewsets.ModelViewSet):
    """
    """
    queryset            = NotificationEntityTemplate.objects.all()
    serializer_class    = NotificationEntityTypeSerializer
    permission_classes  = (IsAdminOrReadOnly, )
    
