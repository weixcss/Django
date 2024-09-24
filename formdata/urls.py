from django.urls import path
from django.conf import settings
from . import views

urlpatterns = [ 
    path(r'', views.show_form, name="show_form"), ## default url (http://127.0.0.1:8000/formdata/) views.show_form runs function show_form

    # when website reaches this link (http://127.0.0.1:8000/formdata/submit) 
    # views.submit runs function submit which processes the form submission using the POST method to show "formdata/confirmation.html" template
    path(r'submit', views.submit, name="submit"), 
]
