from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone



#  QUẢN LÝ NGƯỜI DÙNG 

class CustomerProfile(models.Model):
    # Liên kết 1-1 với bảng User 
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', verbose_name="Tài khoản")
    fullname = models.CharField(max_length=100, verbose_name="Họ và tên")
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Số điện thoại")
    avatar = models.ImageField(upload_to='avatars/', default='avatars/default.png', verbose_name="Ảnh đại diện")
    
    #   ai Loại da
    SKIN_TYPE_CHOICES = [
        ('unknown', 'Chưa xác định'),
        ('oily', 'Da dầu'),
        ('dry', 'Da khô'),
        ('combination', 'Da hỗn hợp'),
        ('normal', 'Da thường'),
        ('sensitive', 'Da nhạy cảm'),
    ]
    skin_type = models.CharField(max_length=20, choices=SKIN_TYPE_CHOICES, default='unknown', verbose_name="Loại da")
    skin_concerns = models.JSONField(default=list, blank=True, verbose_name="Vấn đề về da (JSON)") # Lưu dạng ['Mụn', 'Nám']

    ROLE_CHOICES = [
        (0, 'Khách hàng'),
        (1, 'Admin'),
        (2, 'Nhân viên'),
    ]
    role = models.IntegerField(choices=ROLE_CHOICES, default=0, verbose_name="Vai trò")
    status = models.BooleanField(default=True, verbose_name="Trạng thái hoạt động")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username

class UserAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    receiver_name = models.CharField(max_length=100, verbose_name="Tên người nhận")
    phone = models.CharField(max_length=20, verbose_name="SĐT")
    city = models.CharField(max_length=100, verbose_name="Tỉnh/Thành")
    district = models.CharField(max_length=100, verbose_name="Quận/Huyện")
    detail_address = models.CharField(max_length=255, verbose_name="Địa chỉ chi tiết")
    is_default = models.BooleanField(default=False, verbose_name="Mặc định")

    def __str__(self):
        return f"{self.receiver_name} - {self.detail_address}"


#  SẢN PHẨM & KHO HÀNG 

class Brand(models.Model):
    name = models.CharField(max_length=100, verbose_name="Tên thương hiệu")
    slug = models.SlugField(unique=True, blank=True, null=True)
    origin = models.CharField(max_length=50, blank=True, verbose_name="Xuất xứ")
    logo = models.ImageField(upload_to='brands/', blank=True, null=True)
    description = models.TextField(blank=True, verbose_name="Mô tả")

    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Tên danh mục")
    slug = models.SlugField(unique=True, blank=True, null=True)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Danh mục cha")
    image = models.ImageField(upload_to='categories/', blank=True, null=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, verbose_name="Danh mục")
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, verbose_name="Thương hiệu")
    
    name = models.CharField(max_length=255, verbose_name="Tên sản phẩm")
    slug = models.SlugField(unique=True, blank=True, null=True)
    sku = models.CharField(max_length=50, unique=True, verbose_name="Mã SKU")
    
    price = models.DecimalField(max_digits=15, decimal_places=0, verbose_name="Giá gốc")
    sale_price = models.DecimalField(max_digits=15, decimal_places=0, default=0, verbose_name="Giá khuyến mãi")
    
    image = models.ImageField(upload_to='products/', verbose_name="Ảnh đại diện")
    gallery = models.JSONField(default=list, blank=True, verbose_name="Album ảnh (JSON)") # Lưu danh sách đường dẫn ảnh phụ
    
    #  AI phù hợp da & thành phần
    target_skin_type = models.CharField(max_length=50, default='Mọi loại da', verbose_name="Phù hợp loại da")
    main_ingredients = models.TextField(blank=True, verbose_name="Thành phần chính")
    usage_instructions = models.TextField(blank=True, verbose_name="Hướng dẫn sử dụng")
    description = models.TextField(blank=True, verbose_name="Mô tả chi tiết")
    
    # Thông số kho & hiển thị
    stock_quantity = models.IntegerField(default=0, verbose_name="Tổng tồn kho")
    sold_quantity = models.IntegerField(default=0, verbose_name="Đã bán")
    views = models.IntegerField(default=0, verbose_name="Lượt xem")
    status = models.BooleanField(default=True, verbose_name="Đang kinh doanh")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class ProductBatch(models.Model):
    
    # Quản lý Date
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='batches')
    batch_code = models.CharField(max_length=50, verbose_name="Mã lô")
    quantity = models.IntegerField(default=0, verbose_name="Số lượng lô này")
    
    manufacturing_date = models.DateField(verbose_name="Ngày sản xuất")
    expiry_date = models.DateField(verbose_name="Hạn sử dụng")
    
    import_price = models.DecimalField(max_digits=15, decimal_places=0, verbose_name="Giá nhập", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Lô {self.batch_code} - {self.product.name}"


#  BÁN HÀNG & ĐƠN HÀNG


class Order(models.Model):
    order_code = models.CharField(max_length=20, unique=True, verbose_name="Mã đơn hàng")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Snapshot thông tin người nhận
    fullname = models.CharField(max_length=100, verbose_name="Người nhận")
    phone = models.CharField(max_length=20, verbose_name="SĐT")
    address = models.CharField(max_length=255, verbose_name="Địa chỉ")
    
    total_money = models.DecimalField(max_digits=15, decimal_places=0, verbose_name="Tổng tiền hàng")
    shipping_fee = models.DecimalField(max_digits=15, decimal_places=0, default=0, verbose_name="Phí ship")
    final_money = models.DecimalField(max_digits=15, decimal_places=0, verbose_name="Thành tiền")
    payment_method = models.CharField(max_length=50, default='COD', verbose_name="PT Thanh toán")
    payment_status = models.BooleanField(default=False, verbose_name="Đã thanh toán")
    
    STATUS_CHOICES = [
        ('pending', 'Chờ xử lý'),
        ('confirmed', 'Đã xác nhận'),
        ('shipping', 'Đang giao'),
        ('completed', 'Hoàn thành'),
        ('cancelled', 'Đã hủy'),
        ('returned', 'Trả hàng'),
    ]
    order_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Trạng thái")
    note = models.TextField(blank=True, verbose_name="Ghi chú")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.order_code} - {self.fullname}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    batch = models.ForeignKey(ProductBatch, on_delete=models.SET_NULL, null=True, verbose_name="Xuất từ Lô")
    product_name = models.CharField(max_length=255, verbose_name="Tên SP (Lưu cứng)")
    quantity = models.IntegerField(default=1, verbose_name="Số lượng")
    price = models.DecimalField(max_digits=15, decimal_places=0, verbose_name="Giá bán lúc mua")

    def __str__(self):
        return f"{self.product_name} x {self.quantity}"


# ĐÁNH GIÁ (REVIEWS)


class Review(models.Model):
    # --- CÁC LỰA CHỌN CHO AI ---
    SENTIMENT_CHOICES = [
        ('POS', 'Tích cực'),
        ('NEU', 'Trung tính'),
        ('NEG', 'Tiêu cực'),
        ('SPAM', 'Spam'),
    ]

    # ---  LIÊN KẾT DỮ LIỆU ---
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, verbose_name="Mua từ đơn")

    # ---  NỘI DUNG ĐÁNH GIÁ ---
    rating = models.IntegerField(default=5, verbose_name="Số sao")
    comment = models.TextField(verbose_name="Bình luận")
    images = models.JSONField(default=list, blank=True, verbose_name="Ảnh feedback (JSON)")

    # ---  KẾT QUẢ TỪ AI  ---
    sentiment = models.CharField(max_length=4, choices=SENTIMENT_CHOICES, default='NEU', verbose_name="Cảm xúc AI")
    confidence_score = models.FloatField(default=0.0, verbose_name="Độ tin cậy AI")

    # ---  SPAM DETECTION ---
    is_spam = models.BooleanField(default=False, verbose_name="Là spam")
    spam_reason = models.CharField(max_length=255, blank=True, verbose_name="Lý do spam")

    # ---  TRẠNG THÁI ---
    # Dùng 'is_approved' của bạn (Thay vì is_hidden của tôi). True = Hiện, False = Ẩn.
    is_approved = models.BooleanField(default=True, verbose_name="Đã duyệt")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"


# ==================== SPAM KEYWORD MODEL ====================
class SpamKeyword(models.Model):
    """Model quản lý danh sách spam keywords"""
    
    CATEGORY_CHOICES = [
        ('FINANCE', 'Tài chính/Cho vay'),
        ('CONTACT', 'Liên hệ/Quảng cáo'),
        ('EXTERNAL', 'Link bên ngoài'),
        ('FAKE', 'Hàng giả/Hàng nhái'),
        ('REPEAT', 'Lặp từ/Spam'),
        ('OTHER', 'Khác'),
    ]
    
    keyword = models.CharField(max_length=255, unique=True, verbose_name="Từ khóa spam")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='OTHER', verbose_name="Danh mục")
    severity = models.IntegerField(default=100, verbose_name="Độ nghiêm trọng (0-100)", 
                                   help_text="100 = Spam chắc chắn, 50 = Nghi ngờ")
    is_active = models.BooleanField(default=True, verbose_name="Kích hoạt")
    description = models.TextField(blank=True, verbose_name="Mô tả", help_text="Giải thích tại sao là spam")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Cập nhật lần cuối")
    
    class Meta:
        verbose_name = "Từ khóa spam"
        verbose_name_plural = "Danh sách từ khóa spam"
        ordering = ['-severity', 'keyword']
    
    def __str__(self):
        return f"{self.keyword} ({self.get_category_display()}) - {self.severity}%"