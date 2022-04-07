from rest_framework.permissions import BasePermission

class HotelOwnerMemberOnly(BasePermission):

    def has_permission(self, request, view): 
        return request.user.groups.filter(name__in=['hotelOwner-gang']).exists()
        