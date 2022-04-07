from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.generic import ListView, View, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic.list import MultipleObjectMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy, reverse 
from django.contrib import messages 
from django.db import transaction 
from django.db.models import Q

from hotels.models import Hotel, Reservation, ImageModel, Comment
from hotels.forms import HotelAddForm, ReservationForm, CommentForm
# Create your views here.

''' Hotel part '''

class HotelListView(ListView):
    http_method_names = ['get']
    template_name = 'hotels/list.html'
    model = Hotel 
    ordering = ['-owner__id']
    queryset = Hotel.objects.prefetch_related('hotel_images')
    # queryset = Hotel.objects.select_related('owner')  
    context_object_name = 'hotel_list'
    paginate_by=8
    paginate_orphans = 0
    page_kwarg = 'page'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)  
        context['address_list'] = set([ x[0].lower() for x in self.queryset.values_list('address') ])
        return context
 

class HotelDetailView(View):

    def get(self, request, *args, **kwargs): 
        hotel = Hotel.objects.prefetch_related('hotel_images').get(owner_id = self.kwargs['pk'])
        # print(hotel.hotel_comments.all() )
        context = {
            # 'hotel':  Hotel.objects.select_related('owner').prefetch_related('hotel_images').get(owner_id = self.kwargs['pk'])
            'hotel':  hotel,
            # 'hotel': Hotel.objects.get(owner_id=self.kwargs['pk'])
            'comment_list':  hotel.hotel_comments.all().order_by('-id')
        }
        return render(request, 'hotels/detail.html', context)

# allow only hoteOwner-gang group members to create hotel
# class 
 
class HotelCreateView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = "hotels.add_hotel"
    raise_exception = False
    permission_denied_message = 'Hacker man'

    def get(self, request, *args, **kwargs):  
        # print(Hotel.objects.filter(owner=request.user))
        if Hotel.objects.filter(owner=request.user).exists():
            messages.warning(request, "Sorry, one owner can only add one hotel data and you've already added your hotel data.")
            return redirect('accounts:profile')
        return render(request, 'hotels/add_hotel.html', {'form': HotelAddForm()})

    def post(self, request, *args, **kwargs):
        form = HotelAddForm(request.POST, request.FILES)

        if form.is_valid(): 
            hotel_obj = Hotel.objects.create(
                owner = self.request.user,
                name = form.cleaned_data.get('name'),
                address = form.cleaned_data.get('address'),
                phone = form.cleaned_data.get('phone'),
                email = form.cleaned_data.get('email'),
                total_rooms = form.cleaned_data.get('total_rooms'),
                room_price = form.cleaned_data.get('room_price'),
                established = form.cleaned_data.get('established'),
                description = form.cleaned_data.get('description'),
                map_link = form.cleaned_data.get('map_link')
            )

            supported_image_format = ['jpg','jpeg','png'] 
            for img in request.FILES.getlist('image'):
                if img.name.split('.')[-1].lower()in supported_image_format:
                    ImageModel.objects.create(hotel=hotel_obj, image=img)
            messages.success(request, 'New hotel data added successfully.')
            return redirect('accounts:profile')
        
        return render(request, 'hotels/add_hotel.html', {'form': form})


class HotelUpdateView(LoginRequiredMixin,SuccessMessageMixin, UpdateView):
    http_method_names = ['get', 'post']
    template_name = 'hotels/update_hotel.html'
    model = Hotel 
    fields = ["name", "address","email", "phone", "total_rooms","available_rooms", "room_price", "established", "description", "map_link"]
    context_object_name ='form'
    pk_url_kwarg = 'pk'
    success_message = "Hotel details updated successfully."
    # success_url = reverse_lazy('hotels:hotel_detail', kwargs={'pk': })

    def dispatch(self, request, *args, **kwargs): 
        if request.user.is_authenticated:
            if not(request.user == self.get_object().owner):
                messages.warning(request, 'Sorry, only the owner account of the hotel can update the data.' )
                return redirect( reverse('hotels:hotel_detail', kwargs={'pk': self.kwargs.get('pk')}) )
            return super().dispatch(request, *args, **kwargs)
        else:
            messages.warning(request,"Sorry user, you need to login first.")
            return redirect('accounts:login')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        for field in form.fields:
            form.fields[field].widget.attrs.update({'class': 'form-control'})
        return form 

    def form_valid(self, form):
        if form.cleaned_data.get('total_rooms')<form.cleaned_data.get('available_rooms'):
            form.add_error('available_rooms', 'Availble rooms cannot be greater than total rooms.')
            return render(self.request, 'hotels/update_hotel.html', {'form': form})
        
        return super().form_valid(form)

class HotelDeleteView( LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = "hotels.delete_hotel" 

    def post(self, request,*args, **kwargs): 
        pk = self.kwargs.get('pk') 
        hotel = get_object_or_404(Hotel, owner=pk)
        messages.success(request, f"{hotel.name} details are deleted successfully.")
        hotel.delete() 
        return JsonResponse({}, status=200)

'''Sorting, searching and filter hotel data'''

class HotelSortView(ListView):
    template_name = 'hotels/sortedHotelList.html'
    model = Hotel
    context_object_name = 'hotel_list' 

    def get_queryset(self): 
        sort_param = self.request.GET.get('sort').strip()
        address_param = self.request.GET.get('address').strip()
        # print(sort_param, address_param)
        
        if sort_param and address_param:
            return Hotel.objects.filter(address__iexact=address_param).order_by(sort_param.lower())
        elif sort_param:
            return Hotel.objects.all().order_by(sort_param.lower())
        elif address_param:
            return Hotel.objects.select_related('owner').filter(address__iexact=address_param).order_by('-owner__id')
        else:
            return Hotel.objects.select_related('owner').all().order_by('-owner__id') 

"""class HotelAddressSelectView(View):
    
    def get(self, request, *args, **kwargs): 
        address = self.request.GET.get('address').strip()
        if address:
            hotel_list =  Hotel.objects.filter(address__iexact=address)
        else:
            hotel_list = Hotel.objects.all()  
        return render(request, 'hotels/sortedHotelList.html',{'hotel_list': hotel_list} )"""

class HotelSearchView(ListView):
    http_method_names = ['get']
    template_name = 'hotels/list.html'
    model = Hotel
    context_object_name = 'hotel_list'
    paginate_by=8
    paginate_orphans = 0
    page_kwarg = 'page'

    def get_queryset(self):
        queryParam = self.request.GET.get('search')
        if queryParam:
            hotel_list = Hotel.objects.filter(Q(name__icontains=queryParam) | Q(description__icontains=queryParam))
        else:
            hotel_list = Hotel.objects.select_related('owner').prefetch_related('hotel_images')
        return hotel_list
 

'''Hotel Booking/Reservation part below''' 

class ReserveHotelView(View):

    def get(self, request,*args, **kwargs): 
        context = {
            'form': ReservationForm(),
            'hotel_pk': self.kwargs.get('pk')
        } 
        return render(request, 'hotels/reserve.html', context)

    def post(self, request, *args, **kwargs):
        form = ReservationForm(request.POST) 
        if form.is_valid():
            data = form.cleaned_data
            hotel_obj = Hotel.objects.get(owner=self.kwargs.get('pk'))
            if data['no_of_rooms'] > hotel_obj.available_rooms:
                form.add_error('no_of_rooms', f'Sorry, only {hotel_obj.available_rooms} rooms are available.')
                return JsonResponse({'errors': form.errors}, status=400) 
            else: 
                try:
                    with transaction.atomic():
                        Reservation.objects.create(
                            no_of_rooms = data['no_of_rooms'],
                            amount = data['no_of_rooms'] * hotel_obj.room_price, 
                            customer = request.user,
                            hotel = hotel_obj,
                            phone = data['phone']
                        )
                        hotel_obj.available_rooms -= int(data['no_of_rooms']) 
                        hotel_obj.save()
                except Exception as e:
                    print(e.__str__())
                    return JsonResponse({'data': e.__str__()}, status=400)

                messages.success(request, 'Hotel room booked successfully.')
                return JsonResponse({'updated_available_rooms': hotel_obj.available_rooms},status=200)
        else: 
            return JsonResponse({'errors': form.errors}, status=400)


''' Comment part '''

class HotelCommentView(LoginRequiredMixin, View):
    
    def post(self, request, *args, **kwargs): 
        form = CommentForm(request.POST)
        if form.is_valid(): 
            hotel = get_object_or_404(Hotel, owner__id= self.kwargs.get('pk') )
            comment = Comment.objects.create(hotel=hotel, customer=request.user, content=form.cleaned_data['content'])
            instance_obj = {
                'customer': request.user.username, 
                'content': form.cleaned_data['content'],
                'date_time': comment.date_time.strftime("%b. %d, %Y, %I:%M %P").replace('am', 'a.m.').replace('pm', 'p.m.')
            } 
            return JsonResponse({ 'instance': instance_obj}, status=200) 

        # print(form.errors)
        return JsonResponse({'errors': form.errors},status=400)