from django.db import models
from django.utils import timezone
from django.urls import reverse
from django.db.models import Q


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
    
    def get_friends(self):
        """
        Returns a list of Profiles that are friends with this profile.
        """
        friends_as_profile1 = Friend.objects.filter(profile1=self).values_list('profile2', flat=True)
        friends_as_profile2 = Friend.objects.filter(profile2=self).values_list('profile1', flat=True)
        
        friend_ids = list(friends_as_profile1) + list(friends_as_profile2)
        return Profile.objects.filter(id__in=friend_ids)
    
    def add_friend(self, other):
        """
        Adds a Friend relationship between this profile and another profile.
        Checks for duplicates and prevents self-friending.
        """
        if self == other:
            return  # Do not allow self-friending
        
        # Check for existing friendship in either direction
        existing_friendship = Friend.objects.filter(
            models.Q(profile1=self, profile2=other) | models.Q(profile1=other, profile2=self)
        ).exists()

        if not existing_friendship:
            # Create the Friend relationship
            Friend.objects.create(profile1=self, profile2=other)

    def get_friend_suggestions(self):
        """
        Returns a list of profiles not currently friends with this profile.
        """
        # Get IDs of current friends
        friends_ids = self.get_friends().values_list('id', flat=True)
        
        # Exclude self and existing friends from suggestions
        return Profile.objects.exclude(id__in=friends_ids).exclude(id=self.id)
    
    def get_news_feed(self):
        """
        Returns a QuerySet of all StatusMessages from the profile and their friends,
        ordered by the most recent.
        """
        # Get friends' profiles as a QuerySet
        friend_profiles = Profile.objects.filter(Q(id__in=[friend.id for friend in self.get_friends()]))

        # Include both self and friend profiles
        profiles = Profile.objects.filter(Q(id=self.id) | Q(id__in=friend_profiles.values_list('id', flat=True)))

        # Gather all status messages for self and friends, ordered by timestamp descending
        return StatusMessage.objects.filter(profile__in=profiles).order_by('-timestamp')

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
    
class Friend(models.Model):
    """
    A model representing a friendship between two profiles.
    
    Attributes:
    - profile1: The first profile in the friendship.
    - profile2: The second profile in the friendship.
    - timestamp: The date/time when the friendship was created.
    """
    profile1 = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="profile1_friends")
    profile2 = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="profile2_friends")
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        """
        String representation of the friendship, showing both profiles' names.
        """
        return f"{self.profile1} & {self.profile2}"