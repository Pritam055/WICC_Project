from this import d
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from hotels.models import Hotel, Reservation, ImageModel, Comment
from accounts.api.serializer import UserRetrieveUpdateSerializer


""" comment part """
class CommentSerializer(serializers.ModelSerializer):
    # customer = serializers.HiddenField(default = serializers.CurrentUserDefault())

    class Meta:
        model = Comment
        fields = ('content', 'customer','hotel')
        read_only_fields = ('customer',)
        
class ImageModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageModel
        fields = ("image",)

class HotelSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False ) 
    class Meta:
        model = Hotel 
        fields = ["owner","name", "address","email", "phone", "total_rooms", "room_price","available_rooms", "established", "description", "image"]
        read_only_fields = ('owner', 'available_rooms',)

class UserInlineSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(read_only=True)

class HotelListSerializer(serializers.ModelSerializer):
    hotel_images = ImageModelSerializer(many=True)  
    owner_info = UserInlineSerializer(source='owner', read_only=True) 

    class Meta:
        model = Hotel 
        fields = ["owner_info","name", "address","email", "phone", "total_rooms", "room_price","available_rooms", "established", "description", "hotel_images"]
        read_only_fields = fields

class HotelRetrieveSerializer(serializers.ModelSerializer):
    hotel_images = ImageModelSerializer(many=True) 
    # owner = serializers.SerializerMethodField(source='owner')
    owner_info = UserInlineSerializer(source='owner', read_only=True)
    hotel_comments = CommentSerializer(many=True)

    class Meta:
        model = Hotel 
        fields = ["owner_info","name", "address","email", "phone", "total_rooms", "room_price","available_rooms", "established", "description", "hotel_images", "hotel_comments"]
        read_only_fields = fields
    
    # def get_owner(self, obj):
    #     return obj.owner.username
     

class HotelUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Hotel 
        fields = [
            # "name", 
            "address",
            "email", 
            "phone", 
            "total_rooms", 
            "room_price", 
            # "established", 
            "description",
            "available_rooms"]

    def validate(self, data): 
        
        if data['total_rooms'] and data['available_rooms']:
            if data['total_rooms'] < data['available_rooms']:
                raise serializers.ValidationError("Available rooms cannot be greater than total rooms.")
        return data
        

""" Reservation part """

class ReservationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Reservation
        fields = ['no_of_rooms', 'hotel', 'payment_method', 'phone' ]
     
    def validate_no_of_rooms(self, value): 
        if value <= 0:
            raise serializers.ValidationError("'no_of_rooms' cannot be <= 0.")
        return value 

    def validate(self, data):  
        if not data.get('no_of_rooms'):
            raise serializers.ValidationError("'no_of_rooms' is required field.")
        else:
            if data['no_of_rooms'] == 0:
                raise serializers.ValidationError("'no_of_rooms' must be greater than 0 while reservation.")
            
            if data['hotel']:
                # print(data['hotel'], type(data['hotel']))
                hotel_obj = get_object_or_404(Hotel, name=data['hotel'])
                if hotel_obj.available_rooms == 0:
                    raise serializers.ValidationError('no rooms are available')
                elif data['no_of_rooms'] > hotel_obj.available_rooms:
                    raise serializers.ValidationError("'no_of_rooms' must be <= 'available rooms'.")
        return data

class ReservationRetrieveSerializer(serializers.ModelSerializer):
    hotel = HotelSerializer()
    customer = UserInlineSerializer()

    class Meta:
        model = Reservation
        fields = ['id','no_of_rooms', 'payment_method', 'phone', 'checkin_status', 'reserved_date', 'checkin_date','checkout_date','amount','paid','customer',  'hotel']
        read_only_fields = ['id',]
    
class CancelReservationSerializer(serializers.Serializer):
    hotelId = serializers.IntegerField()
    reservationId = serializers.IntegerField()

class ReservationUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Reservation
        fields = ['no_of_rooms','customer', 'checkin_status','amount', 'payment_method', 'paid']
        read_only_fields = ('customer',)

    def validate_no_of_rooms(self, value): 
        if value <=0 :  
            raise serializers.ValidationError("'no_of_rooms' cannot be lesser than or equest to 0")
        return value

