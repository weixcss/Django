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
        menu_items = {
            'Pizza': 10,
            'Pasta': 12,
            'Burger': 8,
            'Salad': 15  # Assuming 'Salad' might be a special item sometimes
        }
        ordered_items = request.POST.getlist('menu_item')
        total_price = 0
        item_prices = []
        
        for item in ordered_items:
            if item in menu_items:
                price = menu_items[item]
                total_price += price
                item_prices.append((item, price))  # Collect item and price tuple
        
        customer_info = {
            'name': request.POST.get('name'),
            'phone': request.POST.get('phone'),
            'email': request.POST.get('email')
        }
        ready_time = time.strftime('%H:%M', time.localtime(time.time() + random.randint(1800, 3600)))
        context = {
            'items_ordered': item_prices,  # Pass item and price tuple
            'total_price': total_price,
            'customer_info': customer_info,
            'ready_time': ready_time
        }
        return render(request, 'restaurant/confirmation.html', context)
    else:
        return render(request, 'restaurant/order.html', {'error_message': 'Invalid request method.'})
