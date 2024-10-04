from django.db import models

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
