from django.urls import path
from . import views

urlpatterns = [
    path('', views.quote, name='quotes'),  # http://127.0.0.1:8000/quotes/
    path('quote/', views.quote, name='quote'),  # http://127.0.0.1:8000/quotes/quote
    path('show_all/', views.show_all, name='show_all'),  # http://127.0.0.1:8000/quotes/show_all/
    path('about/', views.about, name='about'),  # http://127.0.0.1:8000/quotes/about/
]