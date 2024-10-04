from django.shortcuts import render

# Create your views here.
from django.views.generic import ListView
from .models import Profile

class ShowAllProfilesView(ListView):
    """
    Class-based view that inherits from Django's ListView to display all existing Profile records from admin.
    
    Attributes:
    - model: used to fetch the data (Profile).
    - template_name: HTML template used to render the view ('mini_fb/show_all_profiles.html').
    - context_object_name: context variable name used in the template ('profiles').
    """
    model = Profile
    template_name = 'mini_fb/show_all_profiles.html'
    context_object_name = 'profiles'