from .cart import Cart

def cart_context(request):
    # Trả về giỏ hàng để sử dụng ở mọi template
    return {'cart': Cart(request)}