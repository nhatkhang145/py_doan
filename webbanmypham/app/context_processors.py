from .cart import Cart
from .models import Wishlist

def cart_context(request):
    # Trả về giỏ hàng để sử dụng ở mọi template
    cart = Cart(request)
    
    # Đếm số sản phẩm trong wishlist (chỉ khi user đã đăng nhập)
    wishlist_count = 0
    if request.user.is_authenticated:
        wishlist_count = Wishlist.objects.filter(user=request.user).count()
    
    return {
        'cart': cart,
        'wishlist_count': wishlist_count
    }