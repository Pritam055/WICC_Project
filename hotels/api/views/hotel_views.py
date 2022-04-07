
from django.contrib.auth import get_user_model
from django.db import transaction

from rest_framework.response import Response 
from rest_framework.views import APIView
from rest_framework import viewsets 
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser

from hotels.models import Hotel, ImageModel, Reservation
from ..serializer import HotelSerializer, HotelUpdateSerializer, HotelListSerializer, HotelRetrieveSerializer, CommentSerializer
from ..permissions import IsAdminOwnerCustomerFilter

CustomUser = get_user_model()

class HotelViewSet(viewsets.ModelViewSet):
    serializer_class = HotelSerializer
    model = Hotel 
    queryset = Hotel.objects.prefetch_related('hotel_images').all().order_by('-owner__id')
    # permission_classes = [ IsAuthenticated, IsAdminOwnerCustomerFilter]
    permission_classes = [IsAdminOwnerCustomerFilter,]
    parser_classes = [MultiPartParser, JSONParser, FormParser]

    def get_serializer_class(self): 
        if self.action == "update": 
            return HotelUpdateSerializer
        elif self.action=="list":
            return HotelListSerializer
        elif self.action == "retrieve":
            return HotelRetrieveSerializer
        return self.serializer_class

    
    # def list(self, request, *args, **kwargs):
    #     queryset = Hotel.objects.prefetch_related('hotel_images').all().order_by('-owner__id')

    #     serializer = GetHotelSerializer(queryset, many=True)
    #     print(serializer.data)
    #     return Response(serializer.data)

    def create(self, request, *args, **kwargs):  
        # print(request.data)
        # print(request.FILES)
        images =  None
        if request.data.get('image'):
            images = request.FILES.getlist('image')  
            request.data.pop('image')
        serializer = self.get_serializer(data=request.data) 

        if not self.request.user.verified:
            return Response({"message": "You're not a verified hotel owner."}, status=status.HTTP_401_UNAUTHORIZED)
        elif Hotel.objects.filter(owner=self.request.user).exists():
            return Response({"message": "A user can have only one hotel."}, status=403)
        
        if serializer.is_valid():
            # hotel_obj = Hotel.objects.create(
            #     owner= request.user,
            #     name = serializer.data.get('name'),
            #     address = serializer.data.get('address'),
            #     email = serializer.data.get('email'),
            #     phone = serializer.data.get('phone'),
            #     total_rooms = serializer.data.get('total_rooms'),
            #     established = serializer.data.get('established'),
            #     description = serializer.data.get('description'),
            # )  
            
            try:
                with transaction.atomic(): 
                    serializer.save( owner = request.user ) 
                    hotel_obj = request.user.hotel 
                    if images:  
                        for img in images:  
                            ImageModel.objects.create(hotel=hotel_obj, image=img)
            except Exception as e: 
                return Response({'err': e.__str__()}, status=status.HTTP_400_BAD_REQUEST)
            return Response({"message": "Hotel objezct created successfully.", "hotel_obj": serializer.data}, status=200)
            
        return Response({"message":"Error occured", "errors": serializer.errors})


    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.owner == self.request.user:
            serializer = self.get_serializer(instance, data=self.request.data )
            
            if serializer.is_valid():
                serializer.save() 
                return Response({"message":"Update success", "updated_data": serializer.data}, status=status.HTTP_200_OK)
            
            return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message": "Sorry, you are not authorized to update others hotel details."}, status=status.HTTP_401_UNAUTHORIZED)

    def destroy(self, request, *args, **kwargs):

        if self.request.user.groups.filter(name__in = ['admin-gang']).exists():
            obj = self.get_object()
            obj.delete()
            return Response({"message":"Deletion success."}, status=status.HTTP_200_OK)
        else: 
            return Response({"message":"Your're not allowed to delete hotel"}, status=status.HTTP_403_FORBIDDEN)

    
class MyHotelView(APIView):
    queryset = Hotel.objects.all()
    serializer_class = HotelRetrieveSerializer
    permission_classes = [IsAuthenticated,]
    
    def get(self, request, *args, **kwargs): 
        if request.user.groups.filter(name__in=['hotelOwner-gang']).exists() and request.user.verified:
            has_hotel = False
            try:
                hotel = Hotel.objects.get(owner = request.user)
                has_hotel = True 
            except Exception as e:
                return Response({'error': e.__str__()})
            serialized = self.serializer_class(hotel)
            return Response(serialized.data, status=status.HTTP_200_OK)

        return Response("Only verified hotelOwner member can retrieve their hotel infomations.", status=status.HTTP_401_UNAUTHORIZED)

""" Comment part """

class CommentModelView( APIView):
    permission_classes = [IsAuthenticated,]
    
    def post(self, request,format=None): 
        # serialized = CommentSerializer(data=request.data, context={'request': request})
        serialized = CommentSerializer(data=request.data )
        if serialized.is_valid():
            serialized.save(customer= request.user)
            return Response({'message': 'comment saved successfully', 'comment': serialized.data}, status=status.HTTP_201_CREATED)
        
        return Response({'errors': serialized.errors}, status=status.HTTP_400_BAD_REQUEST)
