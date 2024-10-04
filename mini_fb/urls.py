from django.urls import path
from . import views
from .views import ShowAllProfilesView


urlpatterns = [
    path('', ShowAllProfilesView.as_view(), name='show_all_profiles'), # http://127.0.0.1:8000/mini_fb/
    #path('', views.main, name='mini_fb'),  # http://127.0.0.1:8000/restaurant/
    #path('main/', views.main, name='main'), # http://127.0.0.1:8000/restaurant/main
    #path('order/', views.order, name='order'), # http://127.0.0.1:8000/restaurant/order
    #path('confirmation/', views.confirmation, name='confirmation'), # http://127.0.0.1:8000/restaurant/confirmation
]
