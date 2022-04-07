from django.urls import path 

from accounts.views import dashboard_views, views
 

app_name = 'accounts'

urlpatterns = [ 
    path('profile/', views.ProfileDetailView.as_view(), name='profile'),
    path('signup/', views.SignupView.as_view(), name='signup'),
    path('login/', views.LoginFormView.as_view(), name='login'),
    path('logout/', views.UserLogoutView.as_view(), name='logout'),
    path('forget-password/', views.ForgotPasswordView.as_view(), name='forget-password' ),
    path('reset-password/<token>/', views.ResetPasswordView.as_view(), name='reset-password'),
    path('update-profile/<int:pk>/', views.UserUpdateView.as_view(), name='update-profile'),

    #payment
    path('verify-payment/', views.VerifyPaymentView.as_view(), name='verify-payment'),

    path('my-certificate/', views.MyCertificateView.as_view(), name='my_certificate'),
    path('add-owner-certificate/', views.AddCertificateView.as_view(), name='add_owner_certificate'),

    path('my-reservations/', views.MyReservationsView.as_view(), name='reservations'),
    path('<int:pk>/my-reservation-details/', views.ReservationDetailView.as_view(), name='reservation_details'),
    path('<int:pk>/cancel-reservation/', views.CancelReservationView.as_view(), name='reservation_cancel'),
    
    path('myhotel/my-hotel-detail/', views.MyHotelDetailView.as_view(), name='my_hotel_detail'),
    path('myhotel/reservation-dashboard/', views.HotelReservationDashboardView.as_view(), name='myhotel_reservation'),
    path('myhotel/filter-reservations/', views.ReservationFilterByOwnerView.as_view(), name='myhotel_filter_reservations'),
    path('myhotel/<int:pk>/customer-reservation-detail/', views.CustomerReservationDetailView.as_view(), name='customer_reservation_detail'),
    path('myhotel/<int:pk>/update-customer-reservation/', views.UpdateCustomerReservationView.as_view(), name='update_customer_reservation'),

    path('dashboard/', dashboard_views.DashboardView.as_view(), name='dashboard'),
    path('dashboard/group-filter/', dashboard_views.GroupUserFilterView.as_view(), name='group_filter'),
    path('dashboard/all-reservations/', dashboard_views.AllReservationView.as_view(), name='all_reservations' ),
    path('dashboard/reservation-hotel-filter/', dashboard_views.ReservationHotelFilterView.as_view(), name='reservation_hotel_filter'),
    path('dashboard/all-hotels/', dashboard_views.AllHotelsView.as_view(), name='all_hotels'),
    path('dashboard/<int:pk>/user-detail/', dashboard_views.DashboardUserDetail.as_view(), name='dashboard_user_detail'),
    path('dashboard/<int:pk>/verify-account/', dashboard_views.VerifyOwnerAccountView.as_view(), name='verify_account'),  

]
