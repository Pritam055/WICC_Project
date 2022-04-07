from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.generic import ListView, DetailView, View, CreateView, FormView, UpdateView
# from django.contrib.messages.views import SuccessMessageMixin 
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin 
# from django.contrib.auth.decorators import permission_required
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy 
from django.contrib.auth.models import Group
from django.contrib import messages
from django.db import transaction
from django.core import serializers
from django.contrib.auth import get_user_model
from django.db.models import Count
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from datetime import datetime
import requests
import json 

# from .models import CustomUser
from accounts.forms import UserForm, UserAuthenticationForm, CertificateForm
from accounts.models import Certificate
from hotels.models import Reservation, Hotel, PAYMENT_METHOD
from accounts.decorators import group_required
from hotels.forms import ReservationUpdateForm


CustomUser = get_user_model()


""" Dashboard part for 'admin-gang' group """

class GroupFilterMixin:
 
    def dispatch(self, request, *args, **kwargs):
        if request.user.groups.filter(name__in=['admin-gang']).exists():
            return super(GroupFilterMixin, self).dispatch(request, *args, **kwargs)
        return HttpResponse("Permission Denied")

# @method_decorator(group_required(['admin-gang']))

class DashboardView(GroupFilterMixin, ListView):

    http_method_names=['get']
    template_name = 'accounts/dashboard/dashboard.html'
    model = CustomUser
    queryset = CustomUser.objects.all().order_by('verified', '-date_joined')
    context_object_name = 'user_list'
    paginate_by=12
    paginate_orphan = 0

    def get_context_data(self,*args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        group_list  = Group.objects.all() 
        context['group_list'] = group_list
        context['admin_gang'] = group_list.get(name='admin-gang').user_set.count()
        context['hotelOwner_gang']=  group_list.get(name='hotelOwner-gang').user_set.count()
        context['customer_gang']=  group_list.get(name='customer-gang').user_set.count()
        return context


class GroupUserFilterView(GroupFilterMixin, View):

    def get(self, request, *args, **kwargs):
        groupParam = request.GET.get('group').strip()
        if groupParam == "":
            user_list = CustomUser.objects.all().order_by('verified', '-date_joined')
        else:
            group_obj = Group.objects.get(name = groupParam)
            user_list = group_obj.user_set.all().order_by('verified', '-date_joined')

        serialized_data = serializers.serialize('json', user_list)
        # print(type(serialized_data))
        # import json 
        # print(type(json.loads(serialized_data)) )
        return JsonResponse({'users': serialized_data}, status=200)

class AllReservationView(GroupFilterMixin, ListView):   
    template_name = 'accounts/dashboard/allReservations.html'
    model = Hotel 
    # context_object_name = 'hotel_list'
    # order_by=['name']
 
    def get_context_data(self, **kwargs):
        context = super(AllReservationView, self).get_context_data(**kwargs) 
        reservations = Reservation.objects.prefetch_related('customer', 'hotel').all()     
        checkin_groupby = reservations.values('checkin_status').annotate(count=Count('id'))
        checkin_groupby_dict =  {x['checkin_status']: x['count'] for x in checkin_groupby}   

        context['hotel_name_list'] = Hotel.objects.values('name').distinct()
        # print(context['hotel_name_list'])
        context['reserved_count'] = checkin_groupby_dict.get('reserved') if checkin_groupby_dict.get('reserved') else 0
        context['checked_in_count'] = checkin_groupby_dict.get('checked_in') if checkin_groupby_dict.get('checked_in') else 0
        context['checked_out_count'] =  checkin_groupby_dict.get('checked_out') if checkin_groupby_dict.get('checked_out') else 0 
        context['reservation_list']= reservations.order_by('-checkin_status','paid', '-reserved_date')  
        return context

class ReservationHotelFilterView(GroupFilterMixin, View):

    def get(self, request, *args, **kwargs): 
        hotelParam = request.GET.get('hotel').strip() 
         
        if hotelParam:
            reservations = Reservation.objects.prefetch_related('customer', 'hotel').filter(hotel__name=hotelParam).order_by('-checkin_status', '-reserved_date')
        else:
            reservations = Reservation.objects.prefetch_related('customer', 'hotel').all().order_by('-checkin_status','paid', '-reserved_date')
          
        # serialized_data = serializers.serialize('json', reservations)
        # return JsonResponse({'reservations': serialized_data}, status=200)
        reservation_list = list() 
        if reservations:
            for r in reservations:
                reservation_list.append({
                    'id':r.id,
                    'customer': r.customer.username,
                    'hotel': r.hotel.name,
                    'no_of_rooms': r.no_of_rooms,
                    'reserved_date':r.reserved_date,
                    'checkin_status': r.checkin_status
                }) 
        return JsonResponse({'data': reservation_list}, status=200)

class DashboardUserDetail(GroupFilterMixin, View):
   
    def get(self, request, *args, **kwargs):
        user_obj = get_object_or_404(CustomUser, id=self.kwargs['pk'])
        has_certificate = False 
            
        if user_obj.groups.filter(name__in=['hotelOwner-gang']).exists():
            try: 
                _ = user_obj.certificate
                has_certificate=True  
            except Exception as e: 
                print(e)  

        # serialized_data = serializers.serialize('json', [user, ])
        # return JsonResponse({'user': serialized_data}, status=200)
        return render(request, 'accounts/dashboard/dashboardUserDetail.html', {
            'user_obj': user_obj,
            'has_certificate': has_certificate
        })

class VerifyOwnerAccountView(GroupFilterMixin, View):
    
    def post(self, request, *args, **kwargs):
        user_obj = get_object_or_404(CustomUser, id=self.kwargs.get('pk'))
        user_obj.verified = True 
        user_obj.save()
        messages.success(request, f"{user_obj.username}'s account is verified successfully.")
        return JsonResponse({},status=200)

class AllHotelsView(GroupFilterMixin, ListView):   
    template_name = 'accounts/dashboard/allHotel.html'
    model = Hotel  
    context_object_name = 'hotel_list' 

    def get_queryset(self):
        return Hotel.objects.select_related('owner').all().order_by('established')
