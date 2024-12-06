from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django import forms
from .models import Customer, Product, Order, OrderItem, Cart, CartItem
import stripe
from django.http import JsonResponse
from django.conf import settings
from django.utils import timezone


# Define the CustomerForm
class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['first_name', 'last_name', 'email', 'address']

# Define the ProductForm (optional for Product Create/Update views)
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'stock_quantity', 'image', 'category']

# Customer Views
class CustomerListView(ListView):
    model = Customer
    template_name = 'weishop/customer_list.html'
    context_object_name = 'customers'

class CustomerDetailView(DetailView):
    model = Customer
    template_name = 'weishop/customer_detail.html'
    context_object_name = 'customer'

class CustomerCreateView(CreateView):
    model = Customer
    form_class = CustomerForm
    template_name = 'weishop/customer_form.html'
    success_url = reverse_lazy('customer_list')

class CustomerUpdateView(UpdateView):
    model = Customer
    form_class = CustomerForm
    template_name = 'weishop/customer_form.html'
    success_url = reverse_lazy('customer_list')

class CustomerDeleteView(DeleteView):
    model = Customer
    template_name = 'weishop/customer_confirm_delete.html'
    success_url = reverse_lazy('customer_list')

# Product Views
class ProductListView(ListView):
    model = Product
    template_name = 'weishop/product_list.html'
    context_object_name = 'products'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=self.request.user)
            context['cart_items'] = cart.cartitem_set.all()
            context['cart_total_price'] = cart.total_price()
        return context

class ProductDetailView(DetailView):
    model = Product
    template_name = 'weishop/product_detail.html'
    context_object_name = 'product'

class ProductCreateView(CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'weishop/product_form.html'
    success_url = reverse_lazy('product_list')

class ProductUpdateView(UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'weishop/product_form.html'
    success_url = reverse_lazy('product_list')

class ProductDeleteView(DeleteView):
    model = Product
    template_name = 'weishop/product_confirm_delete.html'
    success_url = reverse_lazy('product_list')

# Order Views
class OrderListView(ListView):
    model = Order
    template_name = 'weishop/order_list.html'
    context_object_name = 'orders'

class OrderDetailView(DetailView):
    model = Order
    template_name = 'weishop/order_detail.html'
    context_object_name = 'order'

# OrderItem Views (Optional if required in the project)
class OrderItemDetailView(DetailView):
    model = OrderItem
    template_name = 'weishop/orderitem_detail.html'
    context_object_name = 'orderitem'

# Add to Cart
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if product.stock_quantity <= 0:
        return redirect('product_list')

    # Use session-based cart for anonymous users
    if not request.user.is_authenticated:
        cart = request.session.get('cart', {})
        if str(product_id) in cart:
            cart[str(product_id)]['quantity'] += 1
        else:
            cart[str(product_id)] = {
                'name': product.name,
                'price': float(product.price),
                'quantity': 1,
            }
        request.session['cart'] = cart
    else:
        # Handle authenticated users' carts
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            cart_item.quantity += 1
        else:
            cart_item.quantity = 1
        cart_item.save()

    # Reduce the stock quantity
    product.stock_quantity -= 1
    product.save()

    return redirect('cart_view')

# View Cart
def view_cart(request):
    cart_items = []
    total_price = 0

    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_items = cart.cartitem_set.all()
        for item in cart_items:
            item.subtotal = item.product.price * item.quantity
        total_price = sum(item.subtotal for item in cart_items)
    else:
        # Retrieve session-based cart for anonymous users
        cart = request.session.get('cart', {})
        cart_items = [{'name': data['name'], 'price': data['price'], 'quantity': data['quantity'], 
                       'subtotal': data['price'] * data['quantity']} for data in cart.values()]
        total_price = sum(item['subtotal'] for item in cart_items)

    return render(request, 'weishop/cart.html', {
        'cart_items': cart_items,
        'total_price': total_price,
    })

# Remove from Cart
def remove_from_cart(request, cart_item_id):
    cart_item = get_object_or_404(CartItem, id=cart_item_id, cart__user=request.user)

    # Restore the product stock quantity
    cart_item.product.stock_quantity += cart_item.quantity
    cart_item.product.save()

    # Remove the item from the cart
    cart_item.delete()

    return redirect('cart_view')

def checkout(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY

    # Handle authenticated users
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
        cart_items = cart.cartitem_set.all() if cart else []
        line_items = [
            {
                'price_data': {
                    'currency': 'usd',
                    'product_data': {'name': item.product.name},
                    'unit_amount': int(item.product.price * 100),  # Convert dollars to cents
                },
                'quantity': item.quantity,
            }
            for item in cart_items
        ]
    else:
        # Retrieve session-based cart for anonymous users
        cart_data = request.session.get('cart', {})
        cart_items = [
            {'name': data['name'], 'price': data['price'], 'quantity': data['quantity']}
            for data in cart_data.values()
        ]
        line_items = [
            {
                'price_data': {
                    'currency': 'usd',
                    'product_data': {'name': item['name']},
                    'unit_amount': int(item['price'] * 100),  # Convert dollars to cents
                },
                'quantity': item['quantity'],
            }
            for item in cart_items
        ]

    if not line_items:
        return redirect('cart_view')  # Redirect if the cart is empty

    # Create a Stripe Checkout session
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=line_items,
        mode='payment',
        success_url=request.build_absolute_uri('/weishop/checkout/success/'),
        cancel_url=request.build_absolute_uri('/weishop/cart/'),
    )

    return JsonResponse({'id': session.id})

def checkout_success(request):
    if request.user.is_authenticated:
        # Clear the authenticated user's cart
        cart = Cart.objects.filter(user=request.user).first()
        if cart:
            cart.cartitem_set.all().delete()
            cart.delete()
    else:
        # Clear the session-based cart for anonymous users
        request.session.pop('cart', None)

    return render(request, 'weishop/checkout_success.html')