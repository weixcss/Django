from django.shortcuts import render
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django import forms
from .models import Customer, Product, Order, OrderItem

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