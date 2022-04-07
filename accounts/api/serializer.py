from html5lib import serialize
from rest_framework import serializers

from django.contrib.auth import get_user_model 
from django.contrib.auth.models import Group

from accounts.models import Certificate

CustomUser = get_user_model()

class UserSerializer(serializers.ModelSerializer):
 
    class Meta:
        model = CustomUser
        fields = ['email', 'address', 'phone', 'user_type', 'username', 'password']
        extra_kwargs = {'user_type': {'required': True}}

    def create(self, validated_data):  
        pwd = validated_data.pop('password') 
        instance = CustomUser.objects.create(**validated_data)
        instance.set_password(pwd)
        instance.save()
        if instance.user_type == "hotel_owner":
                group_obj = Group.objects.get(name='hotelOwner-gang')
        else:
            instance.verified = True 
            group_obj = Group.objects.get(name='customer-gang')
        instance.groups.add(group_obj)
        instance.save()
        return instance 

class CertificateSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default = serializers.CurrentUserDefault())

    class Meta: 
        model = Certificate
        fields = ('user','image' )
 

class UserRetrieveUpdateSerializer(serializers.ModelSerializer):
    certificate = CertificateSerializer()
    
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'address', 'phone', 'user_type', 'verified', 'certificate']
        read_only_fields = ('certificate', )

class NormalUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = ['email', 'address', 'phone']
    
#password reset part
class ForgetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=254, allow_blank=False)


class PasswordResetSerializer(serializers.Serializer):
    password = serializers.CharField(min_length=5, required=True, write_only=True)
    confirm_password = serializers.CharField(min_length=5, required = True, write_only=True)

    def validate(self, attrs):
        p1 = attrs.get('password')
        p2 = attrs.get('confirm_password')
        if p1 and p2:
            if p1 != p2:
                # raise serializers.ValidationError("Sorry, password and confirm_password doesn't match.")
                raise serializers.ValidationError({'confirm_password': "confirm_password doesn't match with the password"})
        return super().validate(attrs)