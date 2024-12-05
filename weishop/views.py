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
@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if product.stock_quantity <= 0:
        return redirect('product_list')

    # Get or create the user's cart
    cart, created = Cart.objects.get_or_create(user=request.user)

    # Check if the product is already in the cart
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    else:
        cart_item.quantity = 1
        cart_item.save()

    # Reduce the stock quantity
    product.stock_quantity -= 1
    product.save()

    return redirect('cart_view')

# View Cart
@login_required
def view_cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.cartitem_set.all()

    for item in cart_items:
        item.subtotal = item.product.price * item.quantity  # Add subtotal attribute to each item

    total_price = sum(item.subtotal for item in cart_items)  # Calculate total price
    return render(request, 'weishop/cart.html', {
        'cart_items': cart_items,
        'total_price': total_price,
    })

# Remove from Cart
@login_required
def remove_from_cart(request, cart_item_id):
    cart_item = get_object_or_404(CartItem, id=cart_item_id, cart__user=request.user)

    # Restore the product stock quantity
    cart_item.product.stock_quantity += cart_item.quantity
    cart_item.product.save()

    # Remove the item from the cart
    cart_item.delete()

    return redirect('cart_view')

def checkout(request):
    if not request.user.is_authenticated:
        return redirect('login')  # Redirect to login if user is not authenticated

    stripe.api_key = settings.STRIPE_SECRET_KEY

    # Retrieve the user's cart and items
    cart = Cart.objects.filter(user=request.user).first()
    if not cart:
        return redirect('cart_view')  # Redirect if no cart found

    cart_items = cart.cartitem_set.all()
    if not cart_items:
        return redirect('cart_view')  # Redirect if cart is empty

    # Create line items for Stripe
    line_items = []
    for item in cart_items:
        line_items.append({
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': item.product.name,
                },
                'unit_amount': int(item.product.price * 100),  # Convert dollars to cents
            },
            'quantity': item.quantity,
        })

    # Stripe Checkout Session
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=line_items,
        mode='payment',
        success_url=request.build_absolute_uri('/weishop/checkout/success/'),
        cancel_url=request.build_absolute_uri('/weishop/cart/'),
    )
    return JsonResponse({'id': session.id})

def checkout_success(request):
    if not request.user.is_authenticated:
        return redirect('login')  # Ensure user is logged in

    # Retrieve the user's cart
    cart = Cart.objects.filter(user=request.user).first()
    if cart:
        # Create a new Order
        order = Order.objects.create(
            customer=request.user.customer,  # Assuming user has a related customer
            order_date=timezone.now(),
            status='Pending',
            total_price=cart.total_price()
        )

        # Create OrderItems from the cart items
        cart_items = cart.cartitem_set.all()
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                subtotal=item.product.price * item.quantity,
            )

            # Optionally: Reduce product stock (already done when adding to cart)
            # item.product.stock_quantity -= item.quantity
            # item.product.save()

        # Clear the cart
        cart_items.delete()
        cart.delete()

    return render(request, 'weishop/checkout_success.html', {'order': order})