from datetime import datetime 
from django.shortcuts import get_object_or_404
from django.db import transaction

from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from hotels.models import Reservation, Hotel 
from hotels.api.serializer import ReservationSerializer, ReservationRetrieveSerializer, CancelReservationSerializer, ReservationUpdateSerializer
from hotels.api.permissions import IsAdminAndOwnerOnly,HasAllReservationDataPermission


class HotelReservationView(APIView):
    permission_classes = [IsAuthenticated, IsAdminAndOwnerOnly]

    def get(self, request,pk=None, format=None):
        id = pk 
        if id is not None:
            reservation = get_object_or_404(Reservation,id = id) 
            if (request.user == reservation.customer) or request.user.groups.filter(name__in=['admin-gang']) or (request.user == reservation.hotel.owner):
                serialized = ReservationRetrieveSerializer(reservation)
                return Response({'data':serialized.data}, status=status.HTTP_200_OK )
            else:
                return Response({'message':"You're not allowed to view other user's data."}, status=status.HTTP_403_FORBIDDEN)
        else:
            reservations = request.user.customer_reservations.select_related('customer', 'hotel').all().order_by('-id')
            serialized = ReservationRetrieveSerializer(reservations, many=True)
            return Response({'count': len(reservations), 'data': serialized.data}, status=status.HTTP_200_OK )

    def post(self, request, format=None): 
        serializer = ReservationSerializer(data=request.data)
        if serializer.is_valid():   
            hotel_obj = get_object_or_404(Hotel,owner=serializer.data['hotel']) 

            obj = Reservation.objects.create(
                no_of_rooms =serializer.data['no_of_rooms'],
                hotel = hotel_obj,
                payment_method =  serializer.data['payment_method'],
                phone =  serializer.data['phone'],
                customer = request.user,
                amount = hotel_obj.room_price * serializer.data['no_of_rooms']
            )
            hotel_obj.available_rooms -= serializer.data['no_of_rooms']
            hotel_obj.save()
            serialized = ReservationRetrieveSerializer(obj)
            return Response({'message':'Hotel reserved successfully.', 'reserved_data': serialized.data}, status=status.HTTP_201_CREATED)

        return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk, formate=None): 
        r_obj = get_object_or_404(Reservation, id=pk)  
        initial_no_of_rooms = r_obj.no_of_rooms
        initial_checkin_status = r_obj.checkin_status
        serialized = ReservationUpdateSerializer(r_obj, data=request.data, partial=True)  

        if r_obj.checkin_status=='checked_out' and r_obj.paid:
            # serialized = ReservationRetrieveSerializer(r_obj)
            return Response({'message': 'The user is already checked_out and paid. So, you can only read data.' }, status=status.HTTP_400_BAD_REQUEST)
        else:
            if serialized.is_valid(): 

                try:
                    with transaction.atomic():

                        hotel_obj = r_obj.hotel
                        no_of_rooms_changed = request.data.get('no_of_rooms')
                        if no_of_rooms_changed :     
                            if r_obj.no_of_rooms != request.data.get('no_of_rooms'):
                                total_available = hotel_obj.available_rooms + initial_no_of_rooms
                                if  total_available < request.data.get('no_of_rooms'):
                                    return Response({'message': f" Only {total_available} rooms are available."}, status=status.HTTP_200_OK)

                        serialized.save()    
                        # update no_of_rooms if it is changed
                        if no_of_rooms_changed: 
                            hotel_obj.available_rooms = hotel_obj.available_rooms + initial_no_of_rooms 
                            hotel_obj.available_rooms = hotel_obj.available_rooms - serialized.data['no_of_rooms']  
                            hotel_obj.save()

                        if request.data.get('checkin_status') != initial_checkin_status:
                            if request.data.get('checkin_status') == 'checked_in':
                                r_obj.checkin_date = datetime.now()
                            elif request.data.get('checkin_status') == 'checked_out':
                                r_obj.checkout_date = datetime.now() 
                        
                        # if everything is paid and checked_out
                        if r_obj.checkin_status == "checked_out" and r_obj.paid:
                            hotel_obj.available_rooms += r_obj.no_of_rooms
                            hotel_obj.save()
                        r_obj.save() 
                    
                        return Response({'message': 'update success', 'updated_data': serialized.data}, status=status.HTTP_200_OK)
                         
                except Exception as e: 
                    return Response({'error': e.__str__()}) 

            return Response({'errors': serialized.errors}, status=status.HTTP_400_BAD_REQUEST)


class CancelReservationView(APIView):
    permission_classes = [IsAuthenticated,]

    """def post(self, request, format=None):
        serializer = CancelReservationSerializer(data=request.data) 

        if serializer.is_valid(): 
            r_obj = get_object_or_404(Reservation, id=serializer.data['reservationId']) 
            if (r_obj.customer == request.user) or request.user.groups.filter(name__in=["admin-gang"]).exists():
                if r_obj.checkin_status == "reserved":
                    r_obj.hotel.available_rooms += r_obj.no_of_rooms
                    r_obj.hotel.save()
                    r_obj.delete() 
                    return Response({'message': 'Reservation is cancelled successfully.'})
                else:
                    return Response({'message':"Sorry, 'checkin_status' should be 'reserved' inorder to cancel booking."})
            else:
                return Response({'message': "You are not allowed to update other user's reservation data."}, status=status.HTTP_403_FORBIDDEN)
        return Response({}, status=status.HTTP_200_OK)"""
        
    def put(self, request, pk, format=None):  
        r_obj = get_object_or_404(Reservation, id=pk) 
        # print(r_obj.customer == request.user, request.user.groups.filter(name__in=["admin-gang"]).exists(), r_obj.hotel.owner == request.user)

        if (r_obj.customer == request.user) or request.user.groups.filter(name__in=["admin-gang"]).exists() or (r_obj.hotel.owner == request.user):
            if r_obj.checkin_status == "reserved":
                r_obj.hotel.available_rooms += r_obj.no_of_rooms
                r_obj.hotel.save()
                r_obj.delete() 
                return Response({'message': 'Reservation is cancelled successfully.'})
            else:
                return Response({'message':"Sorry, 'checkin_status' should be 'reserved' inorder to cancel booking."})
        else:
            return Response({'message': "You are not allowed to update other user's reservation data."}, status=status.HTTP_403_FORBIDDEN)
        
""" All reservations """

class AllHotelReservationsListAPIView(ListAPIView):
    queryset = Reservation.objects.all()
    permission_classes = [IsAuthenticated, HasAllReservationDataPermission]
    

    def get(self, request, *args, **kwargs):
        if request.user.groups.filter(name__in=['admin-gang']).exists():
            reservation_list = Reservation.objects.all()
        else:
            query_params = request.query_params
            if query_params:
                status = query_params.get('status').strip() if query_params.get('status') else None
                paid = "" 
                paid_param =query_params.get('paid').strip().lower() if query_params.get('paid') else None
                if paid_param:
                    if paid_param=="true":
                        paid = True  
                    elif paid_param=="false":
                        paid=False 

                if status and paid_param:  
                    reservation_list = request.user.hotel.hotel_reservations.filter(checkin_status__iexact=status, paid=paid)
                elif status or paid_param: 
                    if status:
                        reservation_list = request.user.hotel.hotel_reservations.filter(checkin_status__iexact=status )
                    else:
                        reservation_list = request.user.hotel.hotel_reservations.filter(paid=paid )
                else:
                    reservation_list = request.user.hotel.hotel_reservations.all()
            else:
                reservation_list = request.user.hotel.hotel_reservations.all() 

        serialized = ReservationRetrieveSerializer(reservation_list.order_by('-id'), many=True)
        return Response({'count': reservation_list.count(), 'data': serialized.data} )
        