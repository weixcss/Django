from .models import Cart
from django.conf import settings

def cart_context(request):
    cart_items = []
    total_price = 0
    cart_count = 0

    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            cart_items = cart.cartitem_set.all()  # Use cartitem_set to get related CartItem objects
            total_price = sum(item.product.price * item.quantity for item in cart_items)
            cart_count = sum(item.quantity for item in cart_items)  # Calculate total number of items
        except Cart.DoesNotExist:
            cart_items = []

    return {
        'cart_items': cart_items,
        'cart_total_price': total_price,
        'cart_count': cart_count,  # Add cart_count here
    }

def stripe_public_key(request):
    return {
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
    }