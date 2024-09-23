from django.shortcuts import render
import random

quotes = [
    "The biggest risk is not taking any risk... In a world that is changing really quickly, the only strategy that is guaranteed to fail is not taking risks.",
    "Move fast and break things. Unless you are breaking stuff, you are not moving fast enough.",
    "The question isn't, 'What do we want to know about people?', It's, 'What do people want to tell about themselves?'"
]

images = [
    "/static/images/mark1.jpg",
    "/static/images/mark2.jpg",
    "/static/images/mark3.jpg"
]

# View for the main page 
def quote(request):
    selectedQuote = random.choice(quotes)
    selectedImage = random.choice(images)
    context = {
        'quote': selectedQuote,
        'image': selectedImage
    }
    return render(request, 'quote.html', context)

# View for (/quotes/show_all)
def show_all(request):
    context = {
        'quotes': quotes,
        'images': images
    }
    return render(request, 'show_all.html', context)

# View for (/quotes/about)
def about(request):
    return render(request, 'about.html')