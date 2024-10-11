from django import forms
from .models import Profile, StatusMessage

class CreateProfileForm(forms.ModelForm):
    """
    Form to create a new profile with all necessary fields from the Profile model.
    """
    class Meta:
        model = Profile
        fields = ['first_name', 'last_name', 'city', 'email', 'profile_image_url']

class CreateStatusMessageForm(forms.ModelForm):
    """
    Form to create a new status message linked to a profile.
    """
    class Meta:
        model = StatusMessage
        fields = ['message']