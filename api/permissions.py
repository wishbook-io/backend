from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the snippet.
        return obj.user == request.user

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the snippet.
        return request.user.is_staff

class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated()

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.user == request.user or request.user.is_staff

class IsCompanyOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated()

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.company == request.user.companyuser.company or request.user.is_staff

class IsCompanyAdministratorOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated()

    def has_object_permission(self, request, view, obj):
        '''if request.method in permissions.SAFE_METHODS:
            return True'''
        return (request.user.groups.filter(name="administrator").exists()) or request.user.is_staff

class IsCompanyAdministratorOrAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    '''def has_permission(self, request, view):
        return request.user and request.user.is_authenticated()'''

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the administrator or admin.
        try:
            return (request.user.groups.filter(name="administrator").exists() and obj.company == request.user.companyuser.company) or request.user.is_staff
        except Exception as e:
            return False

class IsCompanyAdministratorOrAuthenticateUser(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    def has_permission(self, request, view):
        # ~ expand = request.query_params.get('expand', None)
        # ~ if expand is not None and expand.lower()=="true":
        #if request.method=="GET":
        if view.action=="retrieve":
            return True
        return request.user and request.user.is_authenticated()

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the administrator or admin.
        try:
            return (request.user.groups.filter(name="administrator").exists() and obj.company == request.user.companyuser.company) or request.user.is_staff
        except Exception as e:
            return False

class IsCompanyAdministratorOrAdminOrUserOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    '''def has_permission(self, request, view):
        return request.user and request.user.is_authenticated()'''

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the administrator or admin.
        return obj.user==request.user or (request.user.groups.filter(name="administrator").exists() and obj.company == request.user.companyuser.company) or request.user.is_staff





class IsOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated()

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class HasGroupOrPermission(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated() and request.user.permissions




##### View Wise Permission #####
##UserViewSet
class IsCompanyAdministratorOrAdminOrUser(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the snippet.
        return obj == request.user or (request.user.groups.filter(name="administrator").exists() and obj.companyuser.company == request.user.companyuser.company) or request.user.is_staff

##UserProfileViewSet
class IsCompanyAdministratorOrAdminOrUserObj(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the snippet.
        return obj.user == request.user or (request.user.groups.filter(name="administrator").exists() and obj.companyuser.company == request.user.companyuser.company) or request.user.is_staff

##CompanyViewSet
class IsCompanyAdministratorOrAdminOrReadOnlyObj(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    '''def has_permission(self, request, view):
        return request.user and request.user.is_authenticated()'''

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated()

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the administrator or admin.
        try:
            return (request.user.groups.filter(name="administrator").exists() and obj == request.user.companyuser.company) or request.user.is_staff
        except Exception as e:
            return False

##ProductViewSet
class IsCompanyAdministratorOrAdminOrReadOnlyProductObj(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated()

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the administrator or admin.
        return (request.user.groups.filter(name="administrator").exists() and obj.catalog.company == request.user.companyuser.company) or request.user.is_staff

##BuyerViewSet##SellerViewSet
class IsCompanyAdministratorOrAdminOrReadOnlyBuyerSellerObj(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    '''def has_permission(self, request, view):
        return request.user and request.user.is_authenticated()'''

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the administrator or admin.
        return (request.user.groups.filter(name="administrator").exists() and (obj.selling_company == request.user.companyuser.company or obj.buying_company == request.user.companyuser.company)) or request.user.is_staff

##SalesOrderViewSet##PurchaseOrderViewSet
class IsCompanyAdministratorOrAdminOrUserSalesOrderObj(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the snippet.
        return obj.user == request.user or (request.user.groups.filter(name="administrator").exists() and (obj.seller_company == request.user.companyuser.company or obj.company == request.user.companyuser.company or obj.broker_company == request.user.companyuser.company)) or request.user.is_staff
        #return obj.user == request.user or (obj.seller_company == request.user.companyuser.company or obj.company == request.user.companyuser.company or obj.broker_company == request.user.companyuser.company) or request.user.is_staff

##PushUserViewSet
class IsCompanyAdministratorOrAdminOrUserPushUserObj(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    '''def has_permission(self, request, view):
        return request.user and request.user.is_authenticated()'''

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the administrator or admin.
        return obj.user==request.user or obj.push.user == request.user or (request.user.groups.filter(name="administrator").exists() and obj.push.company == request.user.companyuser.company) or request.user.is_staff

##PushCatalogViewSet##PushProductViewSet##PushSelectionViewSet
class IsCompanyAdministratorOrAdminOrUserPushRelObj(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    '''def has_permission(self, request, view):
        return request.user and request.user.is_authenticated()'''

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the administrator or admin.
        return obj.push.user == request.user or (request.user.groups.filter(name="administrator").exists() and obj.push.company == request.user.companyuser.company) or request.user.is_staff
