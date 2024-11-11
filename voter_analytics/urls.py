# In new_app_name/urls.py
from django.urls import path
from . import views
from .views import VoterListView, VoterDetailView, GraphsView

urlpatterns = [
    path('', VoterListView.as_view(), name='voters'),
    path('voter/<int:pk>/', VoterDetailView.as_view(), name='voter'),
    path('graphs/', views.GraphsView.as_view(), name='graphs'),
]
