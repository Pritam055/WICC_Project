
from django.urls import path 

from . import views 

app_name = 'hotels'

urlpatterns = [ 
    path('', views.HotelListView.as_view(), name='hotel_list'),
    path('sort-hotel/', views.HotelSortView.as_view(), name='hotel_sort' ),
    # path('address/', views.HotelAddressSelectView.as_view(), name='hotel_address' ), 
    path('search/', views.HotelSearchView.as_view(), name='hotel_search'),

    path('add-hotel/', views.HotelCreateView.as_view(), name='hotel_create'),
    path('<int:pk>/detail/', views.HotelDetailView.as_view(), name='hotel_detail'),
    path('<int:pk>/update/', views.HotelUpdateView.as_view(), name='hotel_update'),
    path('<int:pk>/delete/', views.HotelDeleteView.as_view(), name='hotel_delete'),
    path('<int:pk>/comment/', views.HotelCommentView.as_view(), name='hotel_comment'),
    
    path('<int:pk>/reserve/', views.ReserveHotelView.as_view(), name='hotel_reserve'),
    

]
