from django.shortcuts import render

# Create your views here.
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from .models import Profile, StatusMessage, Image
from .forms import CreateProfileForm, CreateStatusMessageForm, UpdateProfileForm
from django.urls import reverse
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm

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
    model = Profile
    form_class = CreateProfileForm
    template_name = 'mini_fb/create_profile_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'user_form' not in context:
            context['user_form'] = UserCreationForm()  # Add UserCreationForm to the context
        return context

    def form_valid(self, form):
        user_form = UserCreationForm(self.request.POST)
        
        if user_form.is_valid():
            # Save the user form and get the user instance
            user = user_form.save()
            # Assign the newly created user to the profile instance
            form.instance.user = user
            return super().form_valid(form)
        else:
            # If user_form is invalid, re-render the template with errors
            return self.render_to_response(self.get_context_data(form=form, user_form=user_form))
    
    def get_success_url(self):
        """
        Returns the URL to the newly created profile.
        """
        return reverse('show_profile', kwargs={'pk': self.object.pk})
    
class UpdateProfileView(LoginRequiredMixin, UpdateView):
    """
    Class-based view to update an existing profile.
    """
    model = Profile
    form_class = UpdateProfileForm
    template_name = 'mini_fb/update_profile_form.html'

    def get_object(self):
        # Find the profile of the currently logged-in user
        return Profile.objects.get(user=self.request.user)

    def get_success_url(self):
        """
        After the profile is updated, redirect to the profile page.
        """
        return reverse('show_profile', kwargs={'pk': self.object.pk})

class CreateStatusMessageView(LoginRequiredMixin, CreateView):
    form_class = CreateStatusMessageForm
    template_name = 'mini_fb/create_status_form.html'

    def get_context_data(self, **kwargs):
        """
        Add the profile to the context so it can be displayed in the template.
        """
        context = super().get_context_data(**kwargs)
        # Retrieve profile based on the logged-in user
        profile = Profile.objects.get(user=self.request.user)
        context['profile'] = profile
        return context

    def form_valid(self, form):
        """
        Handles the form submission and creates a status message with images.
        """
        # Attach the profile of the logged-in user to the status message
        profile = Profile.objects.get(user=self.request.user)
        form.instance.profile = profile  # Assign profile to status message
        
        sm = form.save()  # Save the status message to the database

        # Handle file uploads
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
        # Get profile pk from the logged-in user to redirect to the correct profile page
        profile = Profile.objects.get(user=self.request.user)
        return reverse('show_profile', kwargs={'pk': profile.pk})


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
        profile = Profile.objects.get(user=self.request.user)  # Current logged-in user’s profile
        other_profile = Profile.objects.get(pk=self.kwargs['other_pk'])
        profile.add_friend(other_profile)
        return redirect('show_profile', pk=profile.pk)
    
class ShowFriendSuggestionsView(LoginRequiredMixin, DetailView):
    """
    Displays friend suggestions for a given profile.
    """
    model = Profile
    template_name = 'mini_fb/friend_suggestions.html'
    context_object_name = 'profile'

    def get_object(self):
        # Get the profile for the logged-in user
        return get_object_or_404(Profile, user=self.request.user)

class ShowNewsFeedView(DetailView):
    model = Profile
    template_name = 'mini_fb/news_feed.html'
    context_object_name = 'profile'

    def get_object(self):
        # Get the profile for the logged-in user
        return get_object_or_404(Profile, user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['news_feed'] = self.object.get_news_feed()
        return context