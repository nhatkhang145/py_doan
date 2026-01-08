from django.contrib import admin
from .models import (
    CustomerProfile, UserAddress, Brand, Category, 
    Product, ProductBatch, Order, OrderItem, Review, SpamKeyword
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


# 4. Quản lý Spam Keywords
@admin.register(SpamKeyword)
class SpamKeywordAdmin(admin.ModelAdmin):
    list_display = ('keyword', 'category', 'severity', 'is_active', 'created_at')
    list_filter = ('category', 'is_active', 'severity')
    search_fields = ('keyword', 'description')
    list_editable = ('is_active', 'severity')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Thông tin cơ bản', {
            'fields': ('keyword', 'category', 'severity', 'is_active')
        }),
        ('Chi tiết', {
            'fields': ('description',)
        }),
        ('Thời gian', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related()
    
    actions = ['activate_keywords', 'deactivate_keywords']
    
    def activate_keywords(self, request, queryset):
        count = queryset.update(is_active=True)
        self.message_user(request, f'Đã kích hoạt {count} từ khóa')
    activate_keywords.short_description = 'Kích hoạt từ khóa đã chọn'
    
    def deactivate_keywords(self, request, queryset):
        count = queryset.update(is_active=False)
        self.message_user(request, f'Đã vô hiệu hóa {count} từ khóa')
    deactivate_keywords.short_description = 'Vô hiệu hóa từ khóa đã chọn'


# Đăng ký tất cả vào Admin
admin.site.register(CustomerProfile, CustomerProfileAdmin)
admin.site.register(UserAddress)
admin.site.register(Brand)
admin.site.register(Category)
admin.site.register(Product, ProductAdmin)
admin.site.register(ProductBatch) 
admin.site.register(Order, OrderAdmin)
admin.site.register(Review)