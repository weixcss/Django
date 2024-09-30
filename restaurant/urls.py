from django.urls import path
from . import views

urlpatterns = [
    path('restaurant/', views.quote, name='restaurant'),  # http://127.0.0.1:8000/restaurant/
]