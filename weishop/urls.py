from django.urls import path
from django.shortcuts import redirect  # For redirecting to another page
from . import views

from .views import (
    CustomerListView,
    CustomerDetailView,
    CustomerCreateView,
    CustomerUpdateView,
    CustomerDeleteView,
    ProductListView,
    ProductDetailView,
    ProductCreateView,
    ProductUpdateView,
    ProductDeleteView,
    OrderListView,
    OrderDetailView,
    add_to_cart,
    view_cart,
    remove_from_cart,
    checkout, 
    checkout_success,
)

urlpatterns = [
    # Redirect root URL of the app to the customer list view
    path('', lambda request: redirect('customer_list'), name='weishop_home'),

    # Customer-related URLs
    path('customers/', CustomerListView.as_view(), name='customer_list'),
    path('customers/<int:pk>/', CustomerDetailView.as_view(), name='customer_detail'),
    path('customers/new/', CustomerCreateView.as_view(), name='customer_create'),
    path('customers/<int:pk>/edit/', CustomerUpdateView.as_view(), name='customer_update'),
    path('customers/<int:pk>/delete/', CustomerDeleteView.as_view(), name='customer_delete'),

    # Product-related URLs
    path('products/', ProductListView.as_view(), name='product_list'),
    path('products/<int:pk>/', ProductDetailView.as_view(), name='product_detail'),
    path('products/new/', ProductCreateView.as_view(), name='product_create'),
    path('products/<int:pk>/edit/', ProductUpdateView.as_view(), name='product_update'),
    path('products/<int:pk>/delete/', ProductDeleteView.as_view(), name='product_delete'),

    # Order-related URLs
    path('orders/', OrderListView.as_view(), name='order_list'),
    path('orders/<int:pk>/', OrderDetailView.as_view(), name='order_detail'),

    # Cart-related URLs
    path('cart/', view_cart, name='cart_view'),
    path('cart/add/<int:product_id>/', add_to_cart, name='add_to_cart'),  # Fixed the pattern name
    path('cart/remove/<int:cart_item_id>/', remove_from_cart, name='cart_remove'),

    path('checkout/', checkout, name='checkout'),
    path('checkout/success/', checkout_success, name='checkout_success'),
]