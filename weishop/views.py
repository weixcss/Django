from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django import forms
from .models import Customer, Product, Order, OrderItem, Cart, CartItem
import stripe
from django.http import JsonResponse
from django.conf import settings
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User


# Define the CustomerForm
class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['first_name', 'last_name', 'email', 'address']


# Define the ProductForm
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

class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(max_length=100, required=True, label="First Name")
    last_name = forms.CharField(max_length=100, required=True, label="Last Name")
    address = forms.CharField(widget=forms.Textarea, required=True, label="Address")

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'address', 'password1', 'password2']

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


# Cart and Checkout Operations
def add_to_cart(request, product_id):
    # Retrieve the product or return a 404 if not found
    product = get_object_or_404(Product, id=product_id)

    # Handle session-based cart for anonymous users
    if not request.user.is_authenticated:
        cart = request.session.get('cart', {})

        # Check if the product is already in the cart
        if str(product_id) in cart:
            # Check stock availability before incrementing quantity
            if cart[str(product_id)]['quantity'] + 1 > product.stock_quantity:
                messages.error(request, f"Only {product.stock_quantity} of {product.name} available!")
                return redirect('cart_view')

            # Increment the quantity
            cart[str(product_id)]['quantity'] += 1
        else:
            # Add a new product to the cart
            if product.stock_quantity < 1:
                messages.error(request, f"{product.name} is out of stock!")
                return redirect('product_list')

            cart[str(product_id)] = {
                'name': product.name,
                'price': float(product.price),
                'quantity': 1,
            }

        # Reduce stock quantity for the product
        product.stock_quantity -= 1
        product.save()

        # Save the updated cart back to the session
        request.session['cart'] = cart
        request.session.modified = True  # Ensure session is saved
        messages.success(request, f"{product.name} added to your cart!")

    else:
        # Handle authenticated users' carts
        cart, created = Cart.objects.get_or_create(user=request.user)

        # Check if the product is already in the cart
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

        if not created:
            # Check stock availability before incrementing quantity
            if cart_item.quantity + 1 > product.stock_quantity:
                messages.error(request, f"Only {product.stock_quantity} of {product.name} available!")
                return redirect('cart_view')

            # Increment the quantity
            cart_item.quantity += 1
        else:
            # Add new cart item
            if product.stock_quantity < 1:
                messages.error(request, f"{product.name} is out of stock!")
                return redirect('product_list')

            cart_item.quantity = 1

        # Save the cart item
        cart_item.save()

        # Reduce stock quantity for the product
        product.stock_quantity -= 1
        product.save()

        messages.success(request, f"{product.name} added to your cart!")

    return redirect('cart_view')


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
        # Session-based cart
        cart = request.session.get('cart', {})
        cart_items = [
            {
                'product_id': product_id,
                'name': data['name'],
                'price': data['price'],
                'quantity': data['quantity'],
                'subtotal': data['price'] * data['quantity'],
            }
            for product_id, data in cart.items()
        ]
        total_price = sum(item['subtotal'] for item in cart_items)

    return render(request, 'weishop/cart.html', {
        'cart_items': cart_items,
        'total_price': total_price,
    })


def remove_from_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.user.is_authenticated:
        # Find the cart item by product ID and authenticated user's cart
        cart = Cart.objects.filter(user=request.user).first()
        if cart:
            cart_item = CartItem.objects.filter(cart=cart, product_id=product_id).first()
            if cart_item:
                # Restore the product stock quantity
                product.stock_quantity += cart_item.quantity
                product.save()

                # Remove the item from the cart
                cart_item.delete()
            else:
                messages.error(request, "Item not found in your cart.")
    else:
        # Handle session-based cart for anonymous users
        cart = request.session.get('cart', {})
        if str(product_id) in cart:
            # Restore stock quantity
            product.stock_quantity += cart[str(product_id)]['quantity']
            product.save()

            # Remove the item from the session cart
            del cart[str(product_id)]
            request.session['cart'] = cart
            request.session.modified = True
        else:
            messages.error(request, "Item not found in your cart.")

    messages.success(request, f"{product.name} removed from your cart!")
    return redirect('cart_view')

def checkout(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY

    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
        cart_items = cart.cartitem_set.all() if cart else []
        line_items = [
            {
                'price_data': {
                    'currency': 'usd',
                    'product_data': {'name': item.product.name},
                    'unit_amount': int(item.product.price * 100),
                },
                'quantity': item.quantity,
            }
            for item in cart_items
        ]
    else:
        cart = request.session.get('cart', {})
        line_items = [
            {
                'price_data': {
                    'currency': 'usd',
                    'product_data': {'name': data['name']},
                    'unit_amount': int(data['price'] * 100),
                },
                'quantity': data['quantity'],
            }
            for data in cart.values()
        ]

    if not line_items:
        messages.error(request, "Your cart is empty.")
        return redirect('cart_view')

    # Create a Stripe Checkout session
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=line_items,
        mode='payment',
        success_url=request.build_absolute_uri(reverse('checkout_success')),
        cancel_url=request.build_absolute_uri(reverse('cart_view')),
        customer_email=request.user.email if request.user.is_authenticated else None,  # Prefill email for logged-in users
        billing_address_collection='required',  # Require billing address collection
    )

    # Save the session ID for later verification
    request.session['stripe_session_id'] = session.id
    request.session.modified = True

    return JsonResponse({'id': session.id})

def checkout_success(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    session_id = request.session.get('stripe_session_id')

    if not session_id:
        messages.error(request, "Invalid payment session. No order was created.")
        return render(request, 'weishop/checkout_success.html', {'order': None})

    # Verify the payment status
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        if session.payment_status != "paid":
            messages.error(request, "Payment not completed. No order was created.")
            return render(request, 'weishop/checkout_success.html', {'order': None})
    except stripe.error.StripeError as e:
        messages.error(request, f"Stripe error: {str(e)}")
        return render(request, 'weishop/checkout_success.html', {'order': None})

    # Payment successful; process the order
    billing_details = session.get("customer_details", {})
    email = billing_details.get("email", "")
    name = billing_details.get("name", "")
    address = billing_details.get("address", {})
    
    # Extract specific fields from the Stripe address object
    line1 = address.get("line1", "")
    line2 = address.get("line2", "")
    city = address.get("city", "")
    state = address.get("state", "")
    postal_code = address.get("postal_code", "")
    country = address.get("country", "")

    # Format the address with relevant components
    formatted_address = f"{line1}, {line2}, {city}, {state}, {postal_code}, {country}".strip(", ")

    # Create or update the customer
    if request.user.is_authenticated:
        try:
            customer = request.user.customer.get()
            customer.first_name = name.split(" ")[0] if name else customer.first_name
            customer.last_name = " ".join(name.split(" ")[1:]) if len(name.split(" ")) > 1 else customer.last_name
            customer.email = email
            customer.address = formatted_address or customer.address
            customer.save()
        except Customer.DoesNotExist:
            messages.error(request, "Customer profile is missing.")
            return render(request, 'weishop/checkout_success.html', {'order': None})
    else:
        customer, created = Customer.objects.get_or_create(
            email=email,
            defaults={
                "first_name": name.split(" ")[0] if name else "Guest",
                "last_name": " ".join(name.split(" ")[1:]) if len(name.split(" ")) > 1 else "Buyer",
                "address": formatted_address,
            },
        )

    # Process the order
    cart = request.session.get('cart', {})
    if not cart:
        messages.error(request, "Your cart is empty. No order was created.")
        return render(request, 'weishop/checkout_success.html', {'order': None})

    total_price = sum(item['price'] * item['quantity'] for item in cart.values())
    order = Order.objects.create(
        customer=customer,
        order_date=timezone.now(),
        status='Pending',
        total_price=total_price,
        address=formatted_address,  # Save the address to the order
    )

    # Create OrderItems and adjust stock
    for product_id, data in cart.items():
        product = Product.objects.get(id=product_id)
        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=data['quantity'],
            subtotal=data['price'] * data['quantity'],
        )
        product.stock_quantity -= data['quantity']
        product.save()

    # Clear session cart data
    request.session.pop('cart', None)
    request.session.pop('stripe_session_id', None)
    request.session.modified = True

    messages.success(request, "Your order was successfully placed!")
    return render(request, 'weishop/checkout_success.html', {'order': order})

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {user.username}!")
                return redirect('product_list')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'weishop/login.html', {'form': form})


def user_register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()

            # Create a Customer profile with the extra fields
            Customer.objects.create(
                user=user,
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                email=form.cleaned_data['email'],
                address=form.cleaned_data['address'],
            )

            messages.success(request, "Account created successfully. Please log in.")
            return redirect('login')
        else:
            messages.error(request, "There was an error with your registration.")
    else:
        form = CustomUserCreationForm()
    return render(request, 'weishop/register.html', {'form': form})


@login_required
def user_profile(request):
    try:
        customer = request.user.customer.get()
    except Customer.DoesNotExist:
        messages.error(request, "Customer profile is missing.")
        return redirect('product_list')  

    return render(request, 'weishop/profile.html', {'customer': customer})