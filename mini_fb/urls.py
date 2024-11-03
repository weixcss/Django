from django.urls import path
from . import views
from .views import ShowAllProfilesView, ShowProfilePageView, CreateProfileView, CreateStatusMessageView, UpdateProfileView, DeleteStatusMessageView, UpdateStatusMessageView, CreateFriendView, ShowFriendSuggestionsView, ShowNewsFeedView
from django.contrib.auth import views as auth_views


urlpatterns = [
    # Main profile-related URLs
    path('', ShowAllProfilesView.as_view(), name='show_all_profiles'), # http://127.0.0.1:8000/mini_fb/
    path('profile/<int:pk>', ShowProfilePageView.as_view(), name='show_profile'),
    path('create_profile', CreateProfileView.as_view(), name='create_profile'), 

    # Status message URLs
    path('status/create_status', views.CreateStatusMessageView.as_view(), name='create_status'),
    path('status/<int:pk>/delete', DeleteStatusMessageView.as_view(), name='delete_status'),  # Delete status message by primary key
    path('status/<int:pk>/update', UpdateStatusMessageView.as_view(), name='update_status'),  # Update status message by primary key

    # Profile-related actions URLs without primary key of the profile (for logged-in user only)
    path('profile/update', UpdateProfileView.as_view(), name='update_profile'),  # Update logged-in user's profile
    path('profile/add_friend/<int:other_pk>', CreateFriendView.as_view(), name='add_friend'),  # Add friend with specific primary key
    path('profile/friend_suggestions', ShowFriendSuggestionsView.as_view(), name='friend_suggestions'),  # Friend suggestions for logged-in user
    path('profile/news_feed', ShowNewsFeedView.as_view(), name='news_feed'),  # News feed for logged-in user

    # Authentication URLs
    path('login/', auth_views.LoginView.as_view(template_name='mini_fb/login.html'), name='login'),  # Login page
    path('logout/', auth_views.LogoutView.as_view(template_name='mini_fb/logged_out.html'), name='logout'),  # Logout page
]
