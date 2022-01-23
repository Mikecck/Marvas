from django.urls import path

from . import views

urlpatterns = [
    path('', views.store, name='store'),
    path('cart/', views.cart, name='cart'),
    path('checkout/', views.checkout, name='checkout'),

    path('update_item/', views.update_item, name='update_item'),
    path('process_order/', views.process_order, name='process_order'),
    path('product_detail/<int:pk>', views.ProductDetailView.as_view(), name='product_detail'),

    path('customers/', views.listCustomers),
    path('signin/', views.sign_in)
]