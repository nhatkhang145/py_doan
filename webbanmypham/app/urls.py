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

    path('cart/', views.cart_detail, name='cart_detail'),
    path('update-cart/<int:product_id>/', views.update_cart, name='update_cart'),
    path('remove-from-cart/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),


    path('shop/', views.shop, name='shop'),
    path('search/', views.search, name='search'),
    path('cart/', views.cart_detail, name='cart_detail'),

    path('my-admin/', views.admin_dashboard, name='admin_dashboard'),
    path('my-admin/customers/', views.admin_customers, name='admin_customers'),
    path('my-admin/products/', views.admin_products, name='admin_products'),
    path('my-admin/product/add/', views.admin_product_add, name='admin_product_add'),
    path('my-admin/product/edit/<int:id>/', views.admin_product_edit, name='admin_product_edit'),
    path('my-admin/customer/<int:id>/', views.admin_customer_detail, name='admin_customer_detail'),
    path('my-admin/reviews/', views.admin_reviews, name='admin_reviews'),
    path('submit-review/<int:product_id>/', views.submit_review, name='submit_review'),
    path('my-admin/inventory/', views.admin_inventory_alerts, name='admin_inventory_alerts'),
    
    # Category & Brand Management
    path('my-admin/categories/', views.admin_categories, name='admin_categories'),
    path('my-admin/category/edit/<int:id>/', views.admin_category_edit, name='admin_category_edit'),
    path('my-admin/category/delete/<int:id>/', views.admin_category_delete, name='admin_category_delete'),
    path('my-admin/brands/', views.admin_brands, name='admin_brands'),
    path('my-admin/brand/delete/<int:id>/', views.admin_brand_delete, name='admin_brand_delete'),
    
    # Spam Keywords Management
    path('my-admin/spam-keywords/', views.admin_spam_keywords, name='admin_spam_keywords'),
    path('my-admin/spam-keywords/create/', views.admin_spam_keywords_create, name='admin_spam_keywords_create'),
    path('my-admin/spam-keywords/edit/<int:keyword_id>/', views.admin_spam_keywords_edit, name='admin_spam_keywords_edit'),
    path('my-admin/spam-keywords/toggle/<int:keyword_id>/', views.admin_spam_keywords_toggle, name='admin_spam_keywords_toggle'),
    path('my-admin/spam-keywords/delete/<int:keyword_id>/', views.admin_spam_keywords_delete, name='admin_spam_keywords_delete'),
]





