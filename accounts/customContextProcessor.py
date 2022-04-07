
"""def myReservationCount(request):
    if request.user.is_authenticated:
        return {
            'my_reservationCount': request.user.customer_reservations.filter(checkin_status='reserved').count()
        } 
    return {}
        

def isAdminMember(request):
    if request.user.is_authenticated:
        return {
            'is_adminMember': request.user.groups.filter(name__in=['admin-gang']).exists()
        }
    return {}

def isHotelOwnerMember(request): 
    if request.user.is_authenticated:
        has_hotel = False
        try:
            h = request.user.hotel 
            has_hotel = True 
        except Exception as e:
            # print(e) 
            pass 
        return {
            'is_hotelOwnerMember': request.user.groups.filter(name__in=['hotelOwner-gang']).exists() and has_hotel
        }
    return {}"""

def loggedInUserMember(request): 
    user = request.user 
    if user.is_authenticated: 
        group_list = []
        for g in user.groups.all():
            group_list.append(g.name)
 
        is_hotelOwnerMember = False
        is_adminMember = False  
        if 'hotelOwner-gang' in group_list:
            has_hotel = False 
            try:
                h = user.hotel 
                has_hotel = True 
            except Exception as e:
                # print(e) 
                pass 
            is_hotelOwnerMember = ('hotelOwner-gang' in group_list) and has_hotel
            
        if 'admin-gang' in group_list:
            is_adminMember = True 

        return {
            'is_hotelOwnerMember': is_hotelOwnerMember,
            'is_adminMember': is_adminMember,
            'my_reservationCount': user.customer_reservations.filter(checkin_status='reserved').count()
        }
    return {}