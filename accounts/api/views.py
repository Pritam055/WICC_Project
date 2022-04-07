
# from django.http import JsonResponse 
from hashlib import new
from django.db import IntegrityError
from django.http import JsonResponse 
from rest_framework.response import Response 
from rest_framework import viewsets, status
from rest_framework.views import APIView
# from rest_framework.authtoken.models import Token
# from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAuthenticated 
from rest_framework.parsers import FormParser, MultiPartParser 

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.core.mail import send_mail 
from django.contrib.sites.shortcuts import get_current_site 
from django.conf import settings
from django.urls import reverse 

import uuid

from .serializer import (
    PasswordResetSerializer,
    UserSerializer,
    UserRetrieveUpdateSerializer, 
    NormalUpdateSerializer, 
    CertificateSerializer,
    ForgetPasswordSerializer
)
from .permissions import HotelOwnerMemberOnly
from accounts.models import Certificate

CustomUser = get_user_model()

# class CustomUserModelViewSets(viewsets.ModelViewSet):
#     serializer_class = UserSerializer
#     queryset = CustomUser.objects.all()
#     permission_classes = [IsAuthenticated]


class CustomUserAPIView(APIView):

    def get(self, request, pk=None, format=None):
        param_data = request.query_params  
        # print( Group.objects.get(name__iexact='customer-gang').user_set.all() )a
        id = pk 
        if id is not None: 
            if id==self.request.user.id or request.user.groups.filter(name__in=['admin-gang']).exists(): 
                user_obj = get_object_or_404(CustomUser, id=id)
                serializer = UserRetrieveUpdateSerializer(user_obj)
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response({"message": "Your're not allowed to view other user's data."}, status=status.HTTP_403_FORBIDDEN)

        elif request.user.groups.filter(name__in=['admin-gang']).exists():
            if param_data:
                try:
                    group_filter = param_data.get('group').strip()
                    if group_filter: 
                        users = Group.objects.get(name__iexact=group_filter).user_set.all().order_by('-id')
                    else:
                        users = CustomUser.objects.select_related('certificate').all().order_by('-id')
                except Exception as e:
                    return Response({"error": e.__str__(), "message": f"{group_filter} group doesn't exist"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                users = CustomUser.objects.select_related('certificate').all().order_by('-id')
            
            serializers = UserRetrieveUpdateSerializer(users, many=True)
            return Response({"message":"Users data fetched successfully","count": len(users), "data": serializers.data}, status=status.HTTP_200_OK)
        
        return Response({'message': 'Not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def post(self, request, format=None): 
        if request.user.is_authenticated:
            return Response({'message': 'You need to be logged out before creating new user account.'})
        else:
            serializer = UserSerializer(data=request.data)
            if serializer.is_valid(): 
                serializer.save()
                # user = CustomUser.objects.get(username = serializer.data['username'])
                    # token_obj, _= Token.objects.get_or_create(user = user) 
                # return Response({'token': str(token_obj)}, status=200)
                return Response({'message': 'Account is created successfully'}, status=200)
            return Response({'errors': serializer.errors}, status=403)
    

    def put(self, request,pk, format=None):  

        obj = get_object_or_404(CustomUser,id = pk)
        if request.user.groups.filter(name__in=['admin-gang']).exists():
            serialized = UserRetrieveUpdateSerializer(instance=obj, data=request.data, partial=True)
            if serialized.is_valid():
                serialized.save()
                return Response({'message': 'update success', 'updated_data': serialized.data}, status=status.HTTP_200_OK)
            return Response({'errors': serialized.errors}, status=status.HTTP_400_BAD_REQUEST)
        else:
            if obj == request.user:
                serialized = NormalUpdateSerializer(instance=obj, data=request.data, partial=True)
                if serialized.is_valid():
                    serialized.save()
                    return Response({'message': 'udpate success', 'updated_data': serialized.data}, status=status.HTTP_200_OK)
                return Response({'errors': serialized.errors}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'message': "Sorry, you're not allowed to perform this action."}, status=status.HTTP_401_UNAUTHORIZED)

""" Password Reset """
def send_password_reset_mail(email,protocol, domain, token):
    link = protocol+"://"+ domain + reverse('accounts_api:reset-password', kwargs={'token': token})
    print(link)
    subject = "Your password reset link of YOYO's account" 
    message = f"Hello sir/maa'm, click on the link to reset your password {link}"
    
    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [email,],
        fail_silently=False,
    )

class ForgetPasswordView(APIView):

    def post(self, request, format=None):
        serialized = ForgetPasswordSerializer(data=request.data)
        if serialized.is_valid():
            email = serialized.validated_data.get('email')
            user = CustomUser.objects.filter(email__iexact=email)
            if user.exists():
                user_obj = user.first()
                token = str(uuid.uuid4())
                user_obj.forget_password_token = token 
                user_obj.save()
                current_site = get_current_site(request)
                domain = current_site.domain
                protocol = "http"
                send_password_reset_mail(user_obj.email, protocol, domain, token)
                return JsonResponse({'message': 'Password reset link is sent through mail. Check your password reset mail.'}, status=status.HTTP_200_OK)
            else:
                return JsonResponse({'message': 'User does not exist with this email.'})
        return JsonResponse({'errors': serialized.errors}, status=status.HTTP_400_BAD_REQUEST)        


class ResetPasswordView(APIView):

    def post(self, request, token, format=None):
        user = CustomUser.objects.filter(forget_password_token = token).first()
        print(token)
        print(user)
        if user:
            serialized = PasswordResetSerializer(data = request.data)
            if serialized.is_valid():
                new_password = serialized.validated_data.get('password') 
                user.set_password(new_password)
                user.forget_password_token = None 
                user.save()  
                return JsonResponse({'message': 'Password reset success'}, status=status.HTTP_200_OK)
                
            return JsonResponse({'errors': serialized.errors}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return JsonResponse({'error': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)

class MyAccountView(APIView):
    permission_classes = [IsAuthenticated, ]

    def get(self, request, format=None):
        serialized = UserRetrieveUpdateSerializer(request.user) 
        return Response({'data': serialized.data}, status = status.HTTP_200_OK)


class AddCertificateAPIView(APIView):
    permission_classes = [IsAuthenticated, HotelOwnerMemberOnly,]
    parser_classes = [FormParser, MultiPartParser]

    def post(self, request, *args, **kwargs): 
        # print(request.data.pop('image'))
        serialized = CertificateSerializer(data=request.data, context={'request': request}) 

        # print(request.data, serialized.is_valid())
        if serialized.is_valid(): 
            pass  
            
            ''' method 1 '''
            # obj = Certificate(user=request.user,image=request.data.get('image') ) 
            # obj.save()

            ''' method 2'''
            # serialized.save(user = request.user)
    
            try:
                ''' method 3'''
                serialized.save()
            except IntegrityError as e:
                # print(e.__str__()) 
                return Response({'message': 'You have already uploaded certificate','error': e.__str__()}, status=status.HTTP_403_FORBIDDEN )
            return Response({'message' : 'Certificate added successfully', 'data': serialized.data}, status=status.HTTP_201_CREATED)
        return Response({'errors': serialized.errors}, status=status.HTTP_400_BAD_REQUEST )