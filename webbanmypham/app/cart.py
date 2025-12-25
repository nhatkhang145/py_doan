from decimal import Decimal
from django.conf import settings
from .models import Product

class Cart:
    def __init__(self, request):
        """Khởi tạo giỏ hàng"""
        self.session = request.session
        cart = self.session.get('cart')
        if not cart:
            # Nếu chưa có giỏ hàng trong session, tạo mới
            cart = self.session['cart'] = {}
        self.cart = cart

    def add(self, product, quantity=1):
        """Thêm sản phẩm vào giỏ hoặc cập nhật số lượng"""
        product_id = str(product.id) # Key trong JSON phải là string
        if product_id not in self.cart:
            self.cart[product_id] = {
                'quantity': 0, 
                'price': str(product.sale_price if product.sale_price > 0 else product.price),
                'image': str(product.image.url) if product.image else ''
            }
        
        self.cart[product_id]['quantity'] += quantity
        self.save()

    def remove(self, product):
        """Xóa sản phẩm khỏi giỏ"""
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def save(self):
        """Đánh dấu session đã thay đổi để Django lưu lại"""
        self.session.modified = True

    def __iter__(self):
        """Vòng lặp để lấy chi tiết sản phẩm từ Database khi hiển thị"""
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        cart = self.cart.copy()

        for product in products:
            cart[str(product.id)]['product'] = product

        for item in cart.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def get_total_price(self):
        """Tính tổng tiền cả giỏ hàng"""
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())

    def clear(self):
        """Xóa sạch giỏ hàng (sau khi thanh toán xong)"""
        del self.session['cart']
        self.save()