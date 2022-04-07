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
# from django.core import serializers
from django.contrib.auth import get_user_model
from django.db.models import Count
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt 
from django.core.mail import send_mail 
from django.contrib.sites.shortcuts import get_current_site 

from datetime import datetime
import requests, json, uuid
import os 

# from .models import CustomUser
from accounts.forms import (
    UserForm, 
    UserAuthenticationForm, 
    CertificateForm, 
    UserUpdateForm, 
    UserSetPasswordForm, 
    UserPasswordResetForm
)
from accounts.models import Certificate
from accounts.helpers import send_password_reset_mail
from accounts.decorators import group_required
from hotels.models import Reservation, Hotel
from hotels.forms import ReservationUpdateForm


CustomUser = get_user_model()

""" Mixins """

class UserLogoutCheckMixin: 

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('hotels:hotel_list')
        return super(UserLogoutCheckMixin, self).dispatch(request, *args, **kwargs)


class HotelOwnerOnlyAllowMixin:

    def dispatch(self, request, *args, **kwargs):
        if request.user.groups.filter(name__in=['hotelOwner-gang']).exists():
            return super(HotelOwnerOnlyAllowMixin, self).dispatch(request, *args, **kwargs)
        return HttpResponse("Permission denied")

""" Authentication part """

class SignupView(UserLogoutCheckMixin, CreateView):
    template_name = 'accounts/signup.html'
    form_class = UserForm 
    success_url = reverse_lazy('accounts:login')
    # success_message = "User account was created successfully"

    def post(self, request, *args, **kwargs):
        form = self.get_form() 

        if form.is_valid():
            instance = form.save() 
            if form.cleaned_data.get('user_type') == "hotel_owner":
                group_obj = Group.objects.get(name='hotelOwner-gang')
            else:
                instance.verified = True 
                group_obj = Group.objects.get(name='customer-gang')
            instance.groups.add(group_obj)
            instance.save()
            messages.success(request, "User account was created successfully")    
            return redirect(self.success_url)
        
        return render(request, 'accounts/signup.html', {'form': form}) 


class LoginFormView(UserLogoutCheckMixin, FormView):
    template_name = 'accounts/login.html'
    form_class = UserAuthenticationForm
    success_url = reverse_lazy('hotels:hotel_list')

    def get_success_url(self): 
        next = self.request.GET.get('next') 
        if next:
            return str(self.success_url)+next[1:]
        return str(self.success_url)  

    def form_valid(self, form):
        user = authenticate(username=form.cleaned_data.get('username'), password=form.cleaned_data.get('password'))
        if user:
            login(self.request, user) 
        return super().form_valid(form)
            

class UserLogoutView(LoginRequiredMixin, View):
    def get(self, request):
        logout(request)
        return redirect('accounts:login')

class UserUpdateView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        return render(request, 'accounts/update_profile.html', {
            'form': UserUpdateForm(instance = request.user),
        })

    def post(self, request, *args, **kwargs): 
        form = UserUpdateForm(instance=request.user, data=request.POST)
        print(form.is_valid())
        if form.is_valid():
            form.save()
            print(form.cleaned_data)
            messages.info(request, "Profile updated successfully.")
            return JsonResponse({}, status=200)  

        return JsonResponse({'errors': form.errors}, status=400)

class ResetPasswordView(UserLogoutCheckMixin, View):
    def get(self, request, *args, **kwargs): 
        user = CustomUser.objects.filter(forget_password_token = kwargs.get('token')).first()
        if not user:
            messages.warning(request, 'Invalid token.')
            return redirect('accounts:login')

        return render(request, 'accounts/reset_password.html', {
            'form': UserSetPasswordForm(user)
        })

    def post(self, request, *args, **kwargs):
        user = CustomUser.objects.filter(forget_password_token = kwargs.get('token')).first()
        if user:
            form = UserSetPasswordForm(user, request.POST) 
            if form.is_valid():
                form.save()
                user.forget_password_token = None
                user.save()
                messages.info(request, 'Password reset success.') 
                return redirect('accounts:login') 
            else:
                return render(request, 'accounts/reset_password.html', {
                    'form': form
                })
        else:
            messages.warning(request, 'Invalid token.')
            return redirect('accounts:login')
        

class ForgotPasswordView(UserLogoutCheckMixin, View):

    def get(self, request, *args, **kwargs):
        return render(request, 'accounts/forget_password.html', {
            'form': UserPasswordResetForm()
        })

    def post(self, request, *args, **kwargs):
        form = UserPasswordResetForm(request.POST) 
        if form.is_valid():
            email = form.cleaned_data.get('email')
            user = CustomUser.objects.filter(email__iexact=email) 
            if user.exists():
                user_obj = user.first()
                token = str(uuid.uuid4())
                user_obj.forget_password_token = token
                user_obj.save()  
                # getting current url domain name
                current_site = get_current_site(request)
                # site_name = current_site.name 
                domain = current_site.domain
                protocol = "http"  
                send_password_reset_mail(user_obj.email, protocol, domain, token)
                messages.info(request, 'Password reset link is sent through mail. Check your password reset mail.')
                return redirect('accounts:login')
            else:
                messages.warning(request,'User does not exist with this email.')
         
        return render(request, 'accounts/forget_password.html', {
            'form': form
        }) 

''' Owner Certificate Part '''

class MyCertificateView(View):
    def get(self, request, *args, **kwargs): 
        return render(request, 'accounts/owner/mycerfiticate.html')

class AddCertificateView(HotelOwnerOnlyAllowMixin, View):

    def dispatch(self, request, *args, **kwargs):
        if request.user.verified:
            return HttpResponse("You're already verified user")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        # form = CertificateForm(request=request)
        form = CertificateForm()
        return render(request, 'accounts/owner/addOwnerCertificate.html', {'form': form})

    def post(self, request, *args,**kwargs):
        # form = CertificateForm(request.POST, request.FILES, request=request)
        form = CertificateForm(request.POST, request.FILES)
        print(form.is_valid())
        if form.is_valid():
            certificate_obj = Certificate(user=request.user, image=form.cleaned_data.get('image'))
            certificate_obj.save() 
            messages.success(request, "Certificate added successfully.")
            return JsonResponse({}, status=200)

        print(form.errors)
        return JsonResponse({'errors': form.errors}, status=400)


''' My Profile and My Reservation Part '''

class ProfileDetailView(LoginRequiredMixin, View):
    
    def get(self, request, *args, **kwargs): 
        has_hotel = False 
        has_certificate = False 
        
        if request.user.groups.filter(name__in=['hotelOwner-gang']).exists():
            try:
                _ = request.user.certificate
                has_certificate=True 
                _ = request.user.hotel
                has_hotel = True  
            except Exception as e: 
                print(e.__str__()) 
        
        my_group = "["
        for group in request.user.groups.all():
            my_group += group.name + ", "
        my_group += "]" 

        return render(request, 'accounts/profile.html', {
            'has_hotel': has_hotel,
            'has_certificate': has_certificate,
            'my_group': my_group,
            'payment_public_key': os.environ.get('PAYMENT_PUBLIC_KEY'),
        } )

class MyReservationsView(View):

    def get(self, request, *args, **kwargs):  

        context = {
            'reservation_list': request.user.customer_reservations.all().order_by('-checkin_status','paid', '-reserved_date' )
        }
        return render(request, 'accounts/customer/my_reservations.html', context )


class ReservationDetailView(DetailView):
    http_method_names = ['get']
    pk_url_kwarg = 'pk'
    template_name = 'accounts/customer/reservedDetail.html'
    model = Reservation
    context_object_name = 'reservation'


class CancelReservationView(View):
    
    def post(self, request, *args, **kwargs): 
        obj = Reservation.objects.get(id= self.kwargs.get('pk')) 

        try:
            with transaction.atomic():
                hotel_obj = obj.hotel
                hotel_obj.available_rooms += obj.no_of_rooms
                hotel_obj.save()
                obj.delete()
                messages.success(request, 'Reservation is cancelled successfully.')
        except Exception as e:
            print(e.__str__())
            return JsonResponse({'data': e.__str__()}, status=400)

        return JsonResponse({}, status=200)


class MyHotelDetailView(View):
    
    def get(self, request, *args, **kwargs):
        hotel = request.user.hotel
        return render(request, 'accounts/owner/myHotelDetail.html', {'hotel':hotel} )


""" Hotel Customer Reservation Profile""" 

class HotelReservationDashboardView(HotelOwnerOnlyAllowMixin, View):

    def dispatch(self, request, *args, **kwargs): 
        try:
            _ = self.request.user.hotel  
        except Exception as e:
            print(e)
            return redirect('hotels:hotel_list') 
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):   
        hotel = self.request.user.hotel
        reservation_list = hotel.hotel_reservations.select_related('customer', 'hotel').all().order_by('-checkin_status', '-reserved_date') 
        # print(reservation_list.values('checkin_status').annotate(count=Count('id')))
        checkin_groupby = hotel.hotel_reservations.all().values('checkin_status').annotate(count=Count('id')) 
        checkin_groupby_dict =  {x['checkin_status']: x['count'] for x in checkin_groupby}  
 
        reserved_count = checkin_groupby_dict.get('reserved') if checkin_groupby_dict.get('reserved') else 0
        checked_in_count = checkin_groupby_dict.get('checked_in') if checkin_groupby_dict.get('checked_in') else 0
        checked_out_count =  reservation_list.filter(checkin_status='checked_out', paid=False).count() # checkedout but no paid 
        context = { 
            'reservation_list': reservation_list, 
        
            # 'checkin_pending': checkin_groupby[0]['count'],
            # 'checkin_completed': checkin_groupby[1]['count']
 
            'reserved_count': reserved_count,
            'checked_in_count': checked_in_count,
            # 'checked_out_count': checkin_groupby_dict.get('checked_out') if checkin_groupby_dict.get('checked_out') else 0 
            'checked_out_count': checked_out_count,
            'current_customer_count': reserved_count + checked_in_count + checked_out_count,
            'hotel_name': hotel.name
        }
        return render(request, 'accounts/owner/myCustomerReservations.html', context)

class CustomerReservationDetailView(HotelOwnerOnlyAllowMixin, DetailView):
    http_method_names = ['get']
    pk_url_kwarg = 'pk'
    template_name = 'accounts/owner/customerReservedDetail.html'
    model = Reservation
    context_object_name = 'reservation'

class UpdateCustomerReservationView(HotelOwnerOnlyAllowMixin, UpdateView):
    http_method_names = ['get', 'post']
    pk_url_kwarg = 'pk'
    template_name = 'accounts/owner/updateReservedDetail.html'
    form_class = ReservationUpdateForm
    model = Reservation
    context_object_name = 'form'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['reservationId'] = self.kwargs.get('pk')
        return context

    def form_valid(self, form):  
        instance = self.get_object()
        data = form.cleaned_data 
        hotel_obj = instance.hotel 

        if hotel_obj.available_rooms < data.get('no_of_rooms'):
            form.add_error('no_of_rooms', f'Sorry, only {instance.hotel.available_rooms} are available.')
            return JsonResponse({'errors': form.errors}, status=400)

        if data.get('checkin_status')=="checked_in":
            instance.checkin_date = datetime.now()
        elif data.get('checkin_status') == "checked_out":
            instance.checkout_date = datetime.now()

        instance.checkin_status = data.get('checkin_status')
        if instance.no_of_rooms != data.get('no_of_rooms'):
            hotel_obj.available_rooms += instance.no_of_rooms
            hotel_obj.available_rooms -= data.get('no_of_rooms')
            instance.no_of_rooms = data.get('no_of_rooms')
            hotel_obj.save()

        instance.amount = data.get('amount')
        instance.payment_method = data.get('payment_method')
        instance.paid = data.get('paid')

        if instance.checkin_status=="checked_out" and instance.paid:
            instance.hotel.available_rooms += instance.no_of_rooms
            instance.hotel.save()
        instance.save()  

        # if form.cleaned_data.get('checkin_status')!=instance.checkin_status:
        #     instance.checkin_status = form.cleaned_data.get('checkin_status')
        #     instance.checkin_date = datetime.now()

        # if form.cleaned_data.get('paid'):
        #     instance.paid = True 
        #     instance.checkout_date = datetime.now()
        
        # instance.no_of_rooms = form.cleaned_data.get('no_of_rooms')
        # instance.payment_method = form.cleaned_data.get('payment_method')
        # instance.amount = form.cleaned_data.get('amount')
        # instance.save()

        messages.success(self.request, 'Reservation updated successfully.')
        return JsonResponse({}, status=200)

    def form_invalid(self, form): 
        return super().form_invalid(form)

class ReservationFilterByOwnerView(View):
    
    def get(self, request, *args, **kwargs): 
        status = request.GET.get('status').strip()
        paid = request.GET.get('paid').strip() 
 
        reservations = request.user.hotel.hotel_reservations  
        if status and paid:  
            if paid=="True":
                reservation_list = reservations.filter(checkin_status=status, paid=True) 
            else:
                reservation_list = reservations.filter(checkin_status=status, paid=False)

        elif status=="" and paid=="":
            reservation_list = reservations.all()  
        else: 
            if paid != "":
                if paid=='True':
                    reservation_list = reservations.filter(paid=True)
                else:
                    reservation_list = reservations.filter(paid=False)
            else:
                reservation_list = reservations.filter(checkin_status=status) 

        return render(request, 'accounts/owner/reservationFilteredData.html', {
            'reservation_list': reservation_list
        })


""" Khalti Payment """

@method_decorator(csrf_exempt, name='dispatch')
class VerifyPaymentView(LoginRequiredMixin, View):

    def post(self, request, *args, **kwargs):
        data = request.POST
        # print(type(data), request.POST) 
        
        token = data['token']
        reservation_id = data['product_identity']
        obj = get_object_or_404(Reservation, id=reservation_id) 

        url = "https://khalti.com/api/v2/payment/verify/"
        payload = {
            "token": token,
            # "amount": obj.amount
            "amount": 1000
        }
        key = os.environ.get('PAYMENT_SECRET_KEY')
        headers = {
            "Authorization": "Key " + key
        } 
        response = requests.post(url, payload, headers = headers)
        response_data = json.loads(response.text)
        status_code = response.status_code
        print(response_data)

        if status_code == 400:
            return JsonResponse({'message': response_data['detail']}, status=500)
        
        obj.paid = True 
        obj.payment_method = "online_pay"
        obj.save()
        messages.success(request, 'Online payment success.')
        return JsonResponse(f"Payment Success.", status=200, safe=False)

    