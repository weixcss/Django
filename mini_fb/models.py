from django.db import models
from django.utils import timezone
from django.urls import reverse

# Create your models here.
class Profile(models.Model):
    """
    A model representing a user's profile with personal details.

    Attributes:
    - first_name: first name of user (max 30 characters).
    - last_name: last name of user (max 30 characters).
    - city: city of user (max 50 characters).
    - email: email address of user
    - profile_image_url: image address of user's profile picture
    """
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    city = models.CharField(max_length=50)
    email = models.EmailField()
    profile_image_url = models.URLField()

    def __str__(self):
        """
        Returns a string of the user's first name and last name.
        """
        return f"{self.first_name} {self.last_name}"
    
    def get_status_messages(self):
        """
        Returns all status messages for this profile, ordered by timestamp (most recent first).
        """
        return self.status_messages.all().order_by('-timestamp')
    
    def get_absolute_url(self):
        """
        Returns the URL to view this profile.
        """
        return reverse('show_profile', kwargs={'pk': self.pk})

class StatusMessage(models.Model):
    """
    A model representing a status message posted by a user.

    Attributes:
    - timestamp: the time when the message was created (automatically set).
    - message: the text of the status message.
    - profile: a foreign key that links the message to a user's profile.
    """
    timestamp = models.DateTimeField(default=timezone.now)
    message = models.TextField()
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='status_messages')

    def __str__(self):
        """
        Returns a string of the timestamp and message.
        """
        return f"Message at {self.timestamp}: {self.message}"
    
    def get_images(self):
        """
        Returns all images associated with this status message.
        """
        return self.images.all()  # 'images' comes from related_name in Image model
    
class Image(models.Model):
    """
    Model representing an image uploaded for a status message.
    
    Attributes:
    - image_file: the image file stored in the media directory.
    - status_message: a foreign key linking the image to a specific status message.
    - timestamp: the time the image was uploaded.
    """
    image_file = models.ImageField(upload_to='status_images/')
    status_message = models.ForeignKey('StatusMessage', on_delete=models.CASCADE, related_name='images')
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        """
        Returns the string representation of the image with the timestamp.
        """
        return f"Image uploaded at {self.timestamp}"