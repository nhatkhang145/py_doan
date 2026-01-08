from decimal import Decimal
from django.conf import settings
from .models import Product

class Cart:
    def __init__(self, request):
        """
        Khởi tạo giỏ hàng.
        """
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            # Lưu giỏ hàng trống vào session
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    # Khởi tạo phí ship mặc định nếu chưa có (mặc định là 'fast' - Giao nhanh)
        if 'shipping_method' not in self.session:
            self.session['shipping_method'] = 'fast'

    def add(self, product, quantity=1, override_quantity=False):
        """
        Thêm sản phẩm vào giỏ hoặc cập nhật số lượng.
        """
        product_id = str(product.id)
        
        # Nếu chưa có trong giỏ thì tạo mới
        if product_id not in self.cart:
            # Ưu tiên lấy giá sale nếu có, không thì lấy giá gốc
            price = product.sale_price if product.sale_price > 0 else product.price
            
            self.cart[product_id] = {
                'quantity': 0,
                'price': str(price)  # Chuyển Decimal thành string để lưu vào session JSON
            }
        
        # Cập nhật số lượng
        if override_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity
            
        self.save()

    def save(self):
        # Đánh dấu session đã thay đổi để Django lưu lại
        self.session.modified = True

    def remove(self, product):
        """
        Xóa sản phẩm khỏi giỏ hàng.
        """
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def decrease(self, product):
        """
        Giảm số lượng sản phẩm đi 1.
        Nếu số lượng <= 0 thì xóa luôn khỏi giỏ.
        """
        product_id = str(product.id)
        if product_id in self.cart:
            self.cart[product_id]['quantity'] -= 1
            if self.cart[product_id]['quantity'] <= 0:
                del self.cart[product_id]
            self.save()

    def __iter__(self):
        """
        Lặp qua các item trong giỏ hàng và lấy sản phẩm từ database.
        """
        product_ids = self.cart.keys()
        # Lấy các object Product từ DB
        products = Product.objects.filter(id__in=product_ids)
        
        cart = self.cart.copy()
        
        for product in products:
            cart[str(product.id)]['product'] = product
            
        for item in cart.values():
            # Kiểm tra an toàn: Nếu giá bị rỗng (None) thì coi là 0
            _price = item.get('price')
            if _price is None:
                _price = 0
            
            item['price'] = Decimal(str(_price))
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def __len__(self):
        """
        Đếm tổng số lượng sản phẩm trong giỏ.
        """
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        """
        Tính tổng tiền cả giỏ hàng.
        """
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())

    def clear(self):
        """
        Xóa sạch giỏ hàng (dùng khi đã đặt hàng xong).
        """
        del self.session[settings.CART_SESSION_ID]
        self.save()

    