from django.urls import path
from . import views
from .views import ShowAllProfilesView, ShowProfilePageView, CreateProfileView, CreateStatusMessageView


urlpatterns = [
    path('', ShowAllProfilesView.as_view(), name='show_all_profiles'), # http://127.0.0.1:8000/mini_fb/
    path('profile/<int:pk>', ShowProfilePageView.as_view(), name='show_profile'), # http://
    path('create_profile', CreateProfileView.as_view(), name='create_profile'), # http://
    path('profile/<int:pk>/create_status', CreateStatusMessageView.as_view(), name='create_status'),
    #path('', views.main, name='mini_fb'),  # http://127.0.0.1:8000/restaurant/
    #path('main/', views.main, name='main'), # http://127.0.0.1:8000/restaurant/main
    #path('order/', views.order, name='order'), # http://127.0.0.1:8000/restaurant/order
    #path('confirmation/', views.confirmation, name='confirmation'), # http://127.0.0.1:8000/restaurant/confirmation
]
