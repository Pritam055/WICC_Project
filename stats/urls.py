from django.urls import path 

from stats import views 

app_name = 'stats'

urlpatterns = [ 
    path('', views.HotelOwnerReportView.as_view(), name='report'),
    path('dashboard/reservation-report/', views.DashboardReservationReportView.as_view(), name='dashboard_reservation_report'),

    path('report/one-day-reservation/', views.pdfReportReservation, name='one_day_reservation_report'),
    path('report/reservation-date-pdf/', views.PdfReportReservationView2.as_view(), name='reservation_date_pdf'),
    

]