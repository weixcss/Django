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
        menu_items = request.POST.getlist('menu_item')
        prices = [request.POST.get('item_price_' + item) for item in menu_items]
        ordered_items = list(zip(menu_items, prices))  # This will pair each item with its price

        total_price = sum(float(price) for price in prices if price is not None)

        customer_info = {
            'name': request.POST.get('name'),
            'phone': request.POST.get('phone'),
            'email': request.POST.get('email')
        }
        
        special_instructions = request.POST.get('instructions', 'No special instructions provided.')

        current_time = time.time()
        current_time_converted = time.strftime('%H:%M', time.localtime(current_time))
        ready_time = time.strftime('%H:%M', time.localtime(current_time + random.randint(1800, 3600)))

        context = {
            'current_time': current_time_converted,
            'ordered_items': ordered_items,
            'total_price': total_price,
            'customer_info': customer_info,
            'ready_time': ready_time,
            'special_instructions': special_instructions 
        }
        return render(request, 'restaurant/confirmation.html', context)
    else:
        return render(request, 'restaurant/order.html', {'error_message': 'Invalid request method.'})
