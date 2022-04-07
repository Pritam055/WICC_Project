
from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsAdminOwnerCustomerFilter(BasePermission):

    def has_permission(self, request, view): 
 
        if request.method in SAFE_METHODS:
            return True
        elif request.method == 'DELETE':
            return request.user.groups.filter(name__in=['admin-gang', 'hotelOwner-gang']).exists()
        else:  
            return request.user.groups.filter(name__in=['hotelOwner-gang']).exists()

class IsAdminAndOwnerOnly(BasePermission):

    def has_permission(self, request, view):

        if request.method == 'PUT':
            return request.user.groups.filter(name__in=['admin-gang', 'hotelOwner-gang']).exists()
        return True

class HasAllReservationDataPermission(BasePermission):

    def has_permission(self, request, view):
        return request.user.groups.filter(name__in=['admin-gang', 'hotelOwner-gang']).exists()