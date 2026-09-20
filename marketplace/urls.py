from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    path('farmer/', views.farmer, name='farmer'),
    path('add-crop/', views.add_crop, name='add_crop'),

    path('buyer/', views.buyer, name='buyer'),
    path('buy/<int:crop_id>/', views.buy_crop, name='buy_crop'),

    # Payment
    path('payment/<int:order_id>/', views.payment, name='payment'),

    path('orders/', views.my_orders, name='my_orders'),

    path(
        'update-order-status/<int:order_id>/',
        views.update_order_status,
        name='update_order_status'
    ),

    path('fair-price/', views.fair_price, name='fair_price'),
    path('demand-forecast/', views.demand_forecast, name='demand_forecast'),
    path('smart-matching/', views.smart_matching, name='smart_matching'),
    path('logistics/', views.logistics, name='logistics'),

    path('login/', views.login_user, name='login'),
    path('register/', views.register_user, name='register'),
    path('logout/', views.logout_user, name='logout'),
]