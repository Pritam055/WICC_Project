from django.shortcuts import render
from django.http import JsonResponse
from django.views.generic import View
# from django.db.models.functions import ExtractDay
from django.db.models import Count, Sum
# from django.core import serializers

import datetime

from hotels.models import Hotel, Reservation
from .utils import render_to_pdf
from .forms import PdfGenForm
# Create your views here.

class HotelOwnerReportView(View):

    def get(self, request, *args, **kwargs):
        hotel_obj = Hotel.objects.get(owner=request.user) 
        reservations = hotel_obj.hotel_reservations.all()
        # reserved_grouped = Reservation.objects.values('reserved_date__date').annotate(Count('id'))

        # checkin_data = {
        #     'pending': reservations.filter(checkin_status='pending').count(),
        #     'completed': reservations.filter(checkin_status='completed').count()   
        # }   
        reservation_list = list()
        for r in reservations.order_by('-checkin_status', 'paid'):
            reservation_list.append({
                'customer': r.customer.username,
                'no_of_rooms': r.no_of_rooms,
                'reserved_date': r.reserved_date,
                'checkin_status': r.checkin_status,
                'paid': r.paid,

            }) 

        checkin_groupby = reservations.values('checkin_status').annotate(count=Count('id')) 
        checkin_groupby_dict =  {x['checkin_status']: x['count'] for x in checkin_groupby}  
        
        return JsonResponse({ 
            'checkin_data': list(reservations.values('checkin_status').annotate(Count('id'))),
            'reserved_each_day': list(reservations.values('reserved_date__date').annotate(Count('id'))),
            # 'reservation_list': serializers.serialize('json', reservations)
            'reservation_list': reservation_list,
            'total_count': len(reservation_list),
            'reserved_count':checkin_groupby_dict.get('reserved') if checkin_groupby_dict.get('reserved') else 0,
            'checked_in_count': checkin_groupby_dict.get('checked_in') if checkin_groupby_dict.get('checked_in') else 0,
            'checked_out_count':  checkin_groupby_dict.get('checked_out') if checkin_groupby_dict.get('checked_out') else 0 ,

        }, status=200)


class DashboardReservationReportView(View):

    def get(self, request, *args, **kwargs): 
        reservations = Reservation.objects.select_related('customer').prefetch_related('hotel').all()
        reservation_dates =  [x['reserved_date__date'] for x in reservations.values('reserved_date__date').distinct().order_by('-reserved_date__date')]
 
        return JsonResponse({ 
            'checkin_data': list(reservations.values('checkin_status').annotate(Count('id'))),
            'reserved_each_day': list(reservations.values('reserved_date__date').annotate(Count('id'))),
            'reservation_list': list(reservations.values('hotel__name').annotate(Count('id'))),
            'reservation_dates': reservation_dates
        }, status=200)

#--------------PDF generation
def pdfReportReservation(request):
    urlParam = request.GET.get('reserved-date')
    total_amount = 0   

    if urlParam=="" or urlParam=="all":
        records = Reservation.objects.select_related('customer', 'hotel').all()
    else:
        records = Reservation.objects.select_related('customer', 'hotel').filter(reserved_date__date=urlParam)
    # print(records.order_by('-checkin_date'))
    template_name = "stats/pdf/oneDayReservationPDF.html"
    return render_to_pdf(
        template_name,
        {
            'record': records.order_by('-checkin_date'),
            'datetime': datetime.datetime.now(),
            'total_amount':  records.aggregate(Sum('amount'))['amount__sum'],
            'reserved_date': urlParam
        }
    )

class PdfReportReservationView2(View):

    def get(self, request, *args, **kwargs):  
        form = PdfGenForm(self.request.GET) 

        if form.is_valid():
            fromDate = form.cleaned_data.get('fromDate')
            toDate = form.cleaned_data.get('toDate')

            if fromDate and toDate:
                records = Reservation.objects.filter(reserved_date__date__range=[fromDate, toDate]) 
            elif fromDate or toDate:
                if fromDate: 
                    records = Reservation.objects.select_related('customer', 'hotel').filter(reserved_date__date=fromDate)
                else: 
                    records = Reservation.objects.select_related('customer', 'hotel').filter(reserved_date__date=toDate)
            else: 
                records = Reservation.objects.select_related('customer', 'hotel').all()
           
            template_name = "stats/pdf/oneDayReservationPDF.html"
            return render_to_pdf(
                template_name,
                    {
                        'record': records.order_by('-checkin_date'),
                        'datetime': datetime.datetime.now(),
                        'total_amount':  records.aggregate(Sum('amount'))['amount__sum'],
                        'fromDate': fromDate,
                        'toDate': toDate,
                        'redirect_url': request.get_full_path() 
                    }
                ) 
        return JsonResponse({'errors': form.errors, 'status':200})    