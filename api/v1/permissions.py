from rest_framework import permissions
from api.models import *

class StockV1Permission(permissions.BasePermission):
    def has_permission(self, request, view):
        #print "has_permission"
        return request.user and request.user.is_authenticated() and CompanyUser.objects.filter(user=request.user).exists()

    def has_object_permission(self, request, view, obj):
        #print "has_object_permission"
        if request.method in permissions.SAFE_METHODS:
            return True
            
        return obj.warehouse.company == request.user.companyuser.company
