from django.shortcuts import render

# Create your views here.
from django.views.generic import ListView, DetailView, CreateView
from .models import Profile, StatusMessage
from .forms import CreateProfileForm, CreateStatusMessageForm
from django.urls import reverse

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

# Class to show a single profile
class ShowProfilePageView(DetailView):
    """
    Class-based view that inherits from Django's DetailView to display one Profile record.
    
    Attributes:
    - model: used to fetch the data (Profile).
    - template_name: HTML template used to render the view ('mini_fb/show_profile.html').
    - context_object_name: context variable name used in the template ('profile').
    """
    model = Profile
    template_name = 'mini_fb/show_profile.html'
    context_object_name = 'profile'

class CreateProfileView(CreateView):
    """
    Class-based view that allows users to create a new profile.
    
    Attributes:
    - form_class: form used for creating profiles (CreateProfileForm).
    - template_name: HTML template to render the form ('mini_fb/create_profile_form.html').
    """
    form_class = CreateProfileForm
    template_name = 'mini_fb/create_profile_form.html'
    
    def get_success_url(self):
        """
        Returns the URL to the newly created profile.
        """
        return reverse('show_profile', kwargs={'pk': self.object.pk})
    
class CreateStatusMessageView(CreateView):
    """
    Class-based view to handle creating a status message for a profile.
    """
    form_class = CreateStatusMessageForm
    template_name = 'mini_fb/create_status_form.html'

    def get_context_data(self, **kwargs):
        """
        Add the profile to the context so it can be displayed in the template.
        """
        context = super().get_context_data(**kwargs)
        profile = Profile.objects.get(pk=self.kwargs['pk'])
        context['profile'] = profile
        return context

    def form_valid(self, form):
        """
        Attach the status message to the correct profile before saving.
        """
        profile = Profile.objects.get(pk=self.kwargs['pk'])
        form.instance.profile = profile
        return super().form_valid(form)

    def get_success_url(self):
        """
        Redirect to the profile page after the status message is created.
        """
        return reverse('show_profile', kwargs={'pk': self.kwargs['pk']})