from django.contrib import admin
from django.urls import path
from . import views 

urlpatterns = [
     path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('product/<int:id>/', views.product_detail, name='product_detail'),
   path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
   path('shop/', views.shop, name='shop'),
   path('search/', views.search, name='search'),
   path('cart/', views.cart_detail, name='cart_detail'),

   path('my-admin/', views.admin_dashboard, name='admin_dashboard'),
    path('my-admin/customers/', views.admin_customers, name='admin_customers'),
    path('my-admin/products/', views.admin_products, name='admin_products'),
    path('my-admin/product/add/', views.admin_product_add, name='admin_product_add'),
    path('my-admin/product/edit/<int:id>/', views.admin_product_edit, name='admin_product_edit'),
]





