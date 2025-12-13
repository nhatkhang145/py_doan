from django.contrib import admin
from .models import (
    CustomerProfile, UserAddress, Brand, Category, 
    Product, ProductBatch, Order, OrderItem, Review
)

#  Quản lý Hồ sơ khách hàng
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'fullname', 'phone', 'skin_type', 'role')
    list_filter = ('skin_type', 'role')

#  Quản lý Sản phẩm 
class ProductBatchInline(admin.TabularInline):
    model = ProductBatch
    extra = 1  # Hiện sẵn 1 dòng trống để nhập lô mới

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'sku', 'category', 'brand', 'price', 'stock_quantity', 'status')
    list_filter = ('brand', 'category', 'target_skin_type', 'status')
    search_fields = ('name', 'sku')
    inlines = [ProductBatchInline] # Nhúng bảng Lô hàng vào trong trang Sản phẩm

# 3. Quản lý Đơn hàng & Chi tiết 
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product_name', 'price', 'quantity') # Không cho sửa 

class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_code', 'fullname', 'phone', 'total_money', 'order_status', 'created_at')
    list_filter = ('order_status', 'created_at')
    search_fields = ('order_code', 'phone', 'fullname')
    inlines = [OrderItemInline]

# Đăng ký tất cả vào Admin
admin.site.register(CustomerProfile, CustomerProfileAdmin)
admin.site.register(UserAddress)
admin.site.register(Brand)
admin.site.register(Category)
admin.site.register(Product, ProductAdmin)
admin.site.register(ProductBatch) 
admin.site.register(Order, OrderAdmin)
admin.site.register(Review)