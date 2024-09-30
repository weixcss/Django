from django.shortcuts import render
import random
import time

def main(request):
    return render(request, 'restaurant/main.html')

def order(request):
    specials = ['Pizza', 'Pasta', 'Burger', 'Salad']
    special_item = random.choice(specials)
    context = {'special_item': special_item}
    return render(request, 'restaurant/order.html', context)

def confirmation(request):
    if request.method == 'POST':
        ordered_items = request.POST.getlist('menu_item')
        total_price = sum(float(price) for price in request.POST.getlist('item_price'))
        customer_info = {
            'name': request.POST.get('name'),
            'phone': request.POST.get('phone'),
            'email': request.POST.get('email')
        }
        ready_time = time.strftime('%H:%M', time.localtime(time.time() + random.randint(1800, 3600)))
        context = {
            'ordered_items': ordered_items,
            'total_price': total_price,
            'customer_info': customer_info,
            'ready_time': ready_time
        }
        return render(request, 'restaurant/confirmation.html', context)
    else:
        return render(request, 'restaurant/order.html', {'error_message': 'Invalid request method.'})
