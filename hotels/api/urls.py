from django.urls import path, include 

from rest_framework.routers import DefaultRouter
from rest_framework.authtoken import views as token_views

from hotels.api.views import hotel_views, reservation_views

app_name = 'hotels_api'

router = DefaultRouter()
router.register('', hotel_views.HotelViewSet,basename='hotels' )

urlpatterns = [ 
    path('', include(router.urls)),
    path('comments/add/', hotel_views.CommentModelView.as_view(), name='comment'),
    # path('token/get-my-token/', token_views.obtain_auth_token ),

    path('owner/my-hotel/', hotel_views.MyHotelView.as_view()),
    path('reserve/reservations/', reservation_views.HotelReservationView.as_view()),
    path('reserve/reservations/all/', reservation_views.AllHotelReservationsListAPIView.as_view()), 
    path('reserve/reservations/<int:pk>/', reservation_views.HotelReservationView.as_view()),
    path('reserve/reservations/cancel-reservation/<int:pk>/', reservation_views.CancelReservationView.as_view() ),

    
]