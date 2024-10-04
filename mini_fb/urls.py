from django.urls import path
from . import views

urlpatterns = [
    path('', views.main, name='mini_fb'),  # http://127.0.0.1:8000/mini_fb/
    #path('main/', views.main, name='main'), # http://127.0.0.1:8000/restaurant/main
    #path('order/', views.order, name='order'), # http://127.0.0.1:8000/restaurant/order
    #path('confirmation/', views.confirmation, name='confirmation'), # http://127.0.0.1:8000/restaurant/confirmation
]
