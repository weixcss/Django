from django.shortcuts import render

# Create your views here.
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from .models import Profile, StatusMessage, Image
from .forms import CreateProfileForm, CreateStatusMessageForm, UpdateProfileForm
from django.urls import reverse
from django.shortcuts import redirect

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
    
class UpdateProfileView(UpdateView):
    """
    Class-based view to update an existing profile.
    """
    model = Profile
    form_class = UpdateProfileForm
    template_name = 'mini_fb/update_profile_form.html'

    def get_success_url(self):
        """
        After the profile is updated, redirect to the profile page.
        """
        return reverse('show_profile', kwargs={'pk': self.object.pk})

class CreateStatusMessageView(CreateView):
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
        Handles the form submission and create status message with images.
        """
        profile = Profile.objects.get(pk=self.kwargs['pk'])
        form.instance.profile = profile  # Attach the profile to the status message
        
        sm = form.save() # Save status message to the database

        # Handles file uploads
        files = self.request.FILES.getlist('files')
        for file in files:
            # Create a new Image object for each uploaded file
            image = Image(status_message=sm, image_file=file)
            image.save()

        return super().form_valid(form)

    def get_success_url(self):
        """
        Redirect to the profile page after the status message is created.
        """
        return reverse('show_profile', kwargs={'pk': self.kwargs['pk']})

class DeleteStatusMessageView(DeleteView):
    """
    View to delete a status message.
    """
    model = StatusMessage
    template_name = 'mini_fb/delete_status_form.html'
    context_object_name = 'status_message'

    def get_success_url(self):
        """
        After deleting the status message, redirect to the associated profile's page.
        """
        profile_pk = self.object.profile.pk  # Gets associated profile's primary key
        return reverse('show_profile', kwargs={'pk': profile_pk})
    
class UpdateStatusMessageView(UpdateView):
    """
    View to update a status message.
    """
    model = StatusMessage
    fields = ['message']  # Only allow editing the message field
    template_name = 'mini_fb/update_status_form.html'
    context_object_name = 'status_message'

    def get_success_url(self):
        """
        After updating the status message, redirect to the associated profile's page.
        """
        profile_pk = self.object.profile.pk
        return reverse('show_profile', kwargs={'pk': profile_pk})
    
class CreateFriendView(View):
    """
    View to add a friend relationship between two profiles.
    """
    def dispatch(self, request, *args, **kwargs):
        profile = Profile.objects.get(pk=self.kwargs['pk'])
        other_profile = Profile.objects.get(pk=self.kwargs['other_pk'])
        profile.add_friend(other_profile)
        return redirect('show_profile', pk=profile.pk)
    
class ShowFriendSuggestionsView(DetailView):
    """
    Displays friend suggestions for a given profile.
    """
    model = Profile
    template_name = 'mini_fb/friend_suggestions.html'
    context_object_name = 'profile'

class ShowNewsFeedView(DetailView):
    model = Profile
    template_name = 'mini_fb/news_feed.html'
    context_object_name = 'profile'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['news_feed'] = self.object.get_news_feed()
        return context