from django.shortcuts import render, HttpResponse, redirect

# Create your views here.
def show_form(request):
    '''Show the web page with the form.'''
    template_name = "formdata/show_form.html"
    return render(request, template_name)

def submit(request): # request is the HttpRequest object, <WSGIRequest: POST '/formdata/submit'>
    '''Process the form submission, and generate a result.'''

    template_name = "formdata/confirmation.html"

    if request.POST: #request.POST prints, <QueryDict: {'name': ['John'], 'favorite_color': ['blue']}>
                     #<QueryDict: {'csrfmiddlewaretoken': ['T95JUkwLJoMYv3G8SPfIxKFw6GG6gKBFHYZzTJ0U63AGlTXSZfP4LA7DloLq6wBk'], 'name': ['wei'], 'favorite_color': ['orange']}>
        name = request.POST['name']
        favorite_color = request.POST['favorite_color']
        context = {
            'name': name,
            'favorite_color':  favorite_color,
            
        }
        return render(request, template_name, context=context)

    
    #template_name = "formdata/show_form.html"
    #return render(request, template_name)
    return redirect('show_form') # redirect to the show_form view function, which will render the show_form.html template, url http://127.0.0.1:8000/formdata/