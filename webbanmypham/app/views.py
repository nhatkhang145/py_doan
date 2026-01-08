from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from .forms import RegisterForm, LoginForm
from .models import CustomerProfile, Product, Category, Order, Brand, OrderItem, UserAddress, Review
from .cart import Cart 
from .forms import ProductForm
from datetime import datetime
from .ai_utils import analyze_sentiment
from django.db.models import Avg
import random
from django.db.models import Sum
from datetime import timedelta
from django.utils import timezone

# --- TRANG CHỦ ---
def home(request):
    # 1. Lấy sản phẩm "Gợi ý"
    offer_products = Product.objects.all().order_by('-id')[:8] 
    
    # 2. Lấy sản phẩm "Xu hướng"
    trending_products = Product.objects.filter(sale_price__gt=0)[:8]
    if not trending_products:
        trending_products = Product.objects.all()[:8]

    context = {
        'offer_products': offer_products,
        'trending_products': trending_products
    }
    return render(request, 'app/home.html', context)

# --- ĐĂNG KÝ ---
def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()

            CustomerProfile.objects.create(
                user=user,
                fullname=form.cleaned_data['fullname'],
            )
            
            messages.success(request, "Đăng ký thành công! Hãy đăng nhập.")
            return redirect('login')
        else:
            messages.error(request, "Đăng ký thất bại. Vui lòng kiểm tra lại thông tin.")
    else:
        form = RegisterForm()
    
    return render(request, 'app/register.html', {'form': form})

# --- ĐĂNG NHẬP (Đã sửa lại gọn gàng) ---
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user) # Chỉ cần gọi 1 lần ở đây
                
                # 1. Ưu tiên: Trả về link cũ nếu có
                next_url = request.GET.get('next')
                if next_url:
                    return redirect(next_url)

                # 2. Phân quyền chuyển hướng
                try:
                    user_role = user.profile.role 
                    
                    if user_role == 1: # Admin
                        return redirect('admin_dashboard')
                    elif user_role == 2: # Nhân viên
                        return redirect('admin_dashboard')
                    else: # Khách hàng (role == 0)
                        return redirect('home')
                        
                except Exception as e:
                    # Trường hợp User chưa có Profile (VD: superuser)
                    if user.is_superuser:
                        return redirect('admin_dashboard')
                    return redirect('home')
                
            else:
                messages.error(request, "Sai tên đăng nhập hoặc mật khẩu!")
    else:
        form = LoginForm()
        
    return render(request, 'app/login.html', {'form': form})

# --- ĐĂNG XUẤT ---
def logout_view(request):
    logout(request)
    return redirect('home')

# ---  SẢN PHẨM ---
def shop(request):
    product_list = Product.objects.all().order_by('-id')
    categories = Category.objects.all()
    
    # Lọc theo danh mục nếu có
    active_category = request.GET.get('category')
    if active_category:
        product_list = product_list.filter(category_id=active_category)
    
    # Lọc theo thương hiệu nếu có
    active_brand = request.GET.get('brand')
    if active_brand:
        product_list = product_list.filter(brand_id=active_brand)
    
    # Tạo sidebar_data: danh mục + thương hiệu liên quan
    sidebar_data = []
    for category in categories:
        brands = Brand.objects.filter(product__category=category).distinct()
        sidebar_data.append({
            'category': category,
            'brands': brands
        })
    
    paginator = Paginator(product_list, 12) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'categories': categories,
        'sidebar_data': sidebar_data,
        'active_category': active_category,
        'active_brand': active_brand
    }
    return render(request, 'app/shop.html', context)

# --- CHI TIẾT SẢN PHẨM  ---
def product_detail(request, id):
    product = get_object_or_404(Product, id=id)
    #  sản phẩm liên quan
    related_products = Product.objects.filter(category=product.category).exclude(id=id)[:4]
    
    #  LẤY DANH SÁCH ĐÁNH GIÁ (Chỉ lấy cái đã duyệt: is_approved=True)
    reviews = Review.objects.filter(product=product, is_approved=True).order_by('-created_at')
    
    context = {
        'product': product, 
        'related_products': related_products,
        'reviews': reviews, # <-- Truyền biến này sang HTML
    }
    return render(request, 'app/product_detail.html', context)

# --- THÊM VÀO GIỎ ---
def add_to_cart(request, product_id):
    return redirect('cart_detail')

# --- TÌM KIẾM ---
def search(request):
    if request.method == "GET":
        searched = request.GET.get('searched')
        if searched:
            products = Product.objects.filter(name__icontains=searched)
        else:
            products = []
        return render(request, 'app/search.html', {'searched': searched, 'products': products})

# --- GIỎ HÀNG ---
def add_to_cart(request, product_id):
    cart = Cart(request) # Khởi tạo giỏ hàng
    product = get_object_or_404(Product, id=product_id) # Lấy sản phẩm từ DB
    cart.add(product=product) # Thêm vào giỏ
    return redirect('cart_detail') # Chuyển hướng đến trang giỏ hàng

def cart_detail(request):
    cart = Cart(request)
    return render(request, 'app/cart.html', {'cart': cart})

def update_cart(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.decrease(product)
    return redirect('cart_detail')

def remove_from_cart(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect('cart_detail')


# --- HÀM THANH TOÁN (CHECKOUT) ---
@login_required(login_url='login')
def checkout(request):
    cart = Cart(request)
    
    #  Nếu giỏ hàng trống thì đuổi về trang mua hàng
    if len(cart) == 0:
        messages.warning(request, "Giỏ hàng của bạn đang trống!")
        return redirect('shop')

    #  Xử lý khi bấm nút "ĐẶT HÀNG" (POST)
    if request.method == 'POST':
        # Lấy ID địa chỉ được chọn
        selected_address_id = request.POST.get('selected_address')
        
        fullname = ""
        phone = ""
        address_text = ""
        
        #  A: Người dùng chọn "Nhập địa chỉ mới"
        if selected_address_id == 'new':
            fullname = request.POST.get('fullname')
            phone = request.POST.get('phone')
            # Ghép địa chỉ chi tiết + Tỉnh thành
            address_text = f"{request.POST.get('address')}, {request.POST.get('city')}"
            
        #  B: Người dùng chọn địa chỉ có sẵn
        else:
            try:
                # Lấy địa chỉ từ bảng UserAddress
                addr = UserAddress.objects.get(id=selected_address_id, user=request.user)
                
                # Copy dữ liệu từ bảng UserAddress sang đơn hàng
                fullname = addr.receiver_name  # Khớp với model UserAddress
                phone = addr.phone
                address_text = f"{addr.detail_address}, {addr.district}, {addr.city}"
                
            except UserAddress.DoesNotExist:
                messages.error(request, "Địa chỉ không hợp lệ!")
                return redirect('checkout')

        # Tạo mã đơn hàng ngẫu nhiên (VD: ORD-123456)
        order_code = f"ORD-{random.randint(100000, 999999)}"
        
        # Lấy tổng tiền hàng
        total_price = cart.get_total_price()

        # Lưu đơn hàng vào Database (Bảng Order)
        new_order = Order.objects.create(
            order_code=order_code,
            user=request.user,
            fullname=fullname,     # Tên người nhận
            phone=phone,           # SĐT người nhận
            address=address_text,  # Địa chỉ giao hàng
            
            # --- PHẦN TIỀN NONG (MIỄN PHÍ SHIP) ---
            total_money=total_price,  # Tổng tiền hàng
            shipping_fee=0,           # Phí ship = 0
            final_money=total_price,  # Khách phải trả = Tổng tiền hàng
            # --------------------------------------
            
            payment_method=request.POST.get('payment_method'),
            note=request.POST.get('note')
        )
        
        # Lưu chi tiết sản phẩm vào Database (Bảng OrderItem)
        for item in cart:
            OrderItem.objects.create(
                order=new_order,
                product=item['product'],
                product_name=item['product'].name,
                price=item['price'],
                quantity=item['quantity']
            )
            
        # Xóa giỏ hàng sau khi đặt xong
        cart.clear()
        
        # Thông báo thành công và chuyển hướng
        messages.success(request, f"Đặt hàng thành công! Mã đơn: {order_code}")
        return redirect('home')

    #  Hiển thị trang thanh toán (GET)
    try:
        # Lấy danh sách địa chỉ của người dùng để hiện ra cho họ chọn
        user_addresses = request.user.addresses.all()
    except:
        user_addresses = []
        
    return render(request, 'app/checkout.html', {
        'cart': cart, 
        'user_addresses': user_addresses
    })





# --- LOGIC ADMIN  ---
def is_admin(user):
    try:
        return user.is_superuser or user.profile.role in [1, 2]
    except:
        return False

#  TRANG DASHBOARD (TỔNG QUAN)
@login_required(login_url='login')
@user_passes_test(is_admin, login_url='home')
def admin_dashboard(request):
    # Thống kê cơ bản
    customer_count = CustomerProfile.objects.count()
    product_count = Product.objects.count()
    order_count = Order.objects.count()
    
    # --- LOGIC CẢNH BÁO CHO DASHBOARD (MỚI) ---
    # Đếm nhanh sản phẩm sắp hết (<= 5)
    low_stock_count = Product.objects.filter(stock_quantity__lte=5, status=True).count()
    
    # Đếm nhanh sản phẩm có nguy cơ tồn kho (Tồn > 20)
    # Lưu ý: Đây chỉ là đếm sơ bộ để hiện thông báo, chi tiết sẽ ở trang riêng
    dead_stock_count = Product.objects.filter(stock_quantity__gt=20, status=True).count()

    context = {
        'customer_count': customer_count,
        'product_count': product_count,
        'order_count': order_count,
        'low_stock_count': low_stock_count,       # <--- Biến mới
        'dead_stock_count': dead_stock_count,     # <--- Biến mới
    }
    return render(request, 'app/my_admin/dashboard.html', context)

#  TRANG QUẢN LÝ KHÁCH HÀNG
@login_required(login_url='login')
@user_passes_test(is_admin, login_url='home')
def admin_customers(request):
    customers = CustomerProfile.objects.all()
    context = {'customers': customers}
    return render(request, 'app/my_admin/customers.html', context)

#  TRANG QUẢN LÝ SẢN PHẨM
@login_required(login_url='login')
@user_passes_test(is_admin, login_url='home')
def admin_products(request):
    products_list = Product.objects.all().order_by('-id')
    
    # Lấy dữ liệu cho bộ lọc
    categories = Category.objects.all()
    brands = Brand.objects.all()
    
    paginator = Paginator(products_list, 10) 
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)
    
    context = {
        'products': products,
        'categories': categories,
        'brands': brands, # Truyền thêm brands
    }
    return render(request, 'app/my_admin/products.html', context)


# app/views.py

#  THÊM SẢN PHẨM
@login_required(login_url='login')
@user_passes_test(is_admin, login_url='home')
def admin_product_add(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('admin_products')
    else:
        form = ProductForm()
    
    return render(request, 'app/my_admin/product_form.html', {'form': form, 'title': 'Thêm sản phẩm'})

#  SỬA SẢN PHẨM
@login_required(login_url='login')
@user_passes_test(is_admin, login_url='home')
def admin_product_edit(request, id):
    product = get_object_or_404(Product, id=id)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('admin_products')
    else:
        form = ProductForm(instance=product)
    
    return render(request, 'app/my_admin/product_form.html', {'form': form, 'title': 'Cập nhật sản phẩm'})


#  TRANG CHI TIẾT KHÁCH HÀNG
@login_required(login_url='login')
@user_passes_test(is_admin, login_url='home')
def admin_customer_detail(request, id):
    customer = get_object_or_404(CustomerProfile, id=id)
    # Giả lập dữ liệu đơn hàng (Nếu chưa có model Order)
    recent_orders = [] 
    
    context = {
        'customer': customer,
        'recent_orders': recent_orders
    }
    return render(request, 'app/my_admin/customer_detail.html', context)


#  QUẢN LÝ ĐÁNH GIÁ (REVIEWS)
@login_required(login_url='login')
@user_passes_test(is_admin, login_url='home')
def admin_reviews(request):
    from .services.review_service import is_review_spam
    
    #  Lấy tất cả đánh giá
    reviews = Review.objects.all().order_by('-created_at')
    
    # Tự động phát hiện spam cho reviews chưa được xử lý
    for review in reviews:
        # Dùng getattr với default False cho old reviews chưa có field is_spam
        is_spam_flag = getattr(review, 'is_spam', False)
        if not is_spam_flag and review.comment:  # Chưa được đánh dấu spam
            spam_result = is_review_spam(review.comment, review.rating)
            if spam_result['is_spam']:
                review.is_spam = True
                review.spam_reason = spam_result['reason']
                review.sentiment = 'SPAM'
                review.save()
    
    # Tính toán thống kê (loại bỏ spam)
    valid_reviews = reviews.exclude(is_spam=True)
    total_reviews = valid_reviews.count()
    spam_count = reviews.filter(is_spam=True).count()
    
    pos_percent = 0
    neg_percent = 0
    avg_rating = 0.0
    
    if total_reviews > 0:
        # Đếm số lượng theo cảm xúc (chỉ valid reviews)
        # Dùng getattr để xử lý old reviews không có field sentiment
        pos_count = sum(1 for r in valid_reviews if getattr(r, 'sentiment', 'NEU') == 'POS')
        neg_count = sum(1 for r in valid_reviews if getattr(r, 'sentiment', 'NEU') == 'NEG')
        
        # Tính phần trăm (Làm tròn)
        pos_percent = round((pos_count / total_reviews) * 100)
        neg_percent = round((neg_count / total_reviews) * 100)
        
        # Tính rating trung bình (chỉ valid reviews)
        avg_rating = round(valid_reviews.aggregate(Avg('rating'))['rating__avg'] or 0, 1)
    
    context = {
        'reviews': reviews,
        'total_reviews': total_reviews,
        'spam_count': spam_count,
        'pos_percent': pos_percent,
        'neg_percent': neg_percent,
        'avg_rating': avg_rating
    }
    return render(request, 'app/my_admin/reviews.html', context)

   


#  Hàm xử lý khi khách gửi bình luận
@login_required(login_url='login')
def submit_review(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        
        #  Lấy dữ liệu từ HTML (name="comment")
        
        text_comment = request.POST.get('comment', '').strip()
        rating = request.POST.get('rating')

        # Debug log
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"========== SUBMIT REVIEW ==========")
        logger.info(f"User: {request.user.username}, Product: {product.id}")
        logger.info(f"Comment length: {len(text_comment)}, Rating: {rating}")

        # Kiểm tra comment không rỗng
        if not text_comment:
            logger.warning(f"Empty comment from user {request.user.username}")
            return redirect('product_detail', id=product_id)

        #  Gọi AI phân tích
        logger.info(f"Calling analyze_sentiment...")
        try:
            ai_label, ai_score = analyze_sentiment(text_comment)
            logger.info(f"✓ AI Result - Label: {ai_label}, Score: {ai_score}")
        except Exception as e:
            logger.error(f"✗ AI Error: {e}", exc_info=True)
            ai_label, ai_score = 'NEU', 50.0
        
        # Kiểm tra spam
        from .services.review_service import is_review_spam
        spam_result = is_review_spam(text_comment, int(rating) if rating else 5)
        logger.info(f"Spam check: {spam_result}")

        #  Lưu vào Database
        logger.info(f"Creating review with sentiment={ai_label}, score={ai_score}")
        review = Review.objects.create(
            user=request.user,
            product=product,
            comment=text_comment, 
            rating=rating,
            sentiment=ai_label,
            confidence_score=ai_score,
            is_approved=True, # Tạm thời cho hiện luôn
            is_spam=spam_result['is_spam'],
            spam_reason=spam_result['reason'] if spam_result['is_spam'] else ''
        )
        
        logger.info(f"✓ Review created - ID: {review.id}, Sentiment: {review.sentiment}, Score: {review.confidence_score}")
        
        # Nếu spam thì đổi sentiment thành SPAM
        if spam_result['is_spam']:
            review.sentiment = 'SPAM'
            review.save()
            logger.info(f"✓ Updated to SPAM - ID: {review.id}")
        
        logger.info(f"========== END SUBMIT REVIEW ==========")
        return redirect('product_detail', id=product_id)
    
    
    # 3. THÊM HÀM MỚI QUẢN LÝ CẢNH BÁO KHO (Copy xuống cuối file)
@login_required(login_url='login')
@user_passes_test(is_admin, login_url='home')
def admin_inventory_alerts(request):
    # Cấu hình các ngưỡng (AI Rule-based)
    LOW_STOCK_THRESHOLD = 5       # Dưới 5 là báo hết
    DEAD_STOCK_DAYS = 30          # 30 ngày không bán được
    HIGH_STOCK_THRESHOLD = 20     # Tồn trên 20 mà không bán được là ế

    alerts = []
    
    # Lấy tất cả sản phẩm đang kinh doanh
    products = Product.objects.filter(status=True)
    
    # Thời điểm 30 ngày trước
    time_threshold = timezone.now() - timedelta(days=DEAD_STOCK_DAYS)

    for p in products:
        # --- LOGIC 1: SẮP HẾT HÀNG ---
        if p.stock_quantity <= LOW_STOCK_THRESHOLD:
            alerts.append({
                'product': p,
                'type': 'LOW_STOCK',
                'level': 'critical', 
                'message': 'Sắp hết hàng',
                'suggestion': 'Nhập thêm hàng ngay',
                'icon': 'bx-import',
                'css_class': 'restock'
            })
            continue # Đã báo hết thì bỏ qua báo ế

        # --- LOGIC 2: HÀNG BÁN Ế (Dead Stock) ---
        # Tính tổng số lượng bán trong 30 ngày qua
        recent_sales = OrderItem.objects.filter(
            product=p,
            order__created_at__gte=time_threshold
        ).aggregate(total_sold=Sum('quantity'))['total_sold'] or 0

        # Nếu tồn nhiều (>20) MÀ bán = 0 (hoặc rất ít)
        if p.stock_quantity > HIGH_STOCK_THRESHOLD and recent_sales == 0:
            alerts.append({
                'product': p,
                'type': 'DEAD_STOCK',
                'level': 'warning',
                'message': f'Tồn {p.stock_quantity} nhưng không bán được trong {DEAD_STOCK_DAYS} ngày',
                'suggestion': 'Giảm giá / Flash Sale',
                'icon': 'bxs-offer',
                'css_class': 'discount'
            })

    # Đếm lại chính xác cho trang chi tiết
    total_low = sum(1 for a in alerts if a['type'] == 'LOW_STOCK')
    total_dead = sum(1 for a in alerts if a['type'] == 'DEAD_STOCK')

    # DEBUG: In ra console để kiểm tra
    print(f"=== INVENTORY ALERTS DEBUG ===")
    print(f"Total alerts: {len(alerts)}")
    for alert in alerts[:3]:  # In 3 alert đầu
        print(f"Product: {alert['product'].name}, Type: {alert['type']}")

    context = {
        'alerts': alerts,
        'total_low': total_low,
        'total_dead': total_dead,
    }
    return render(request, 'app/my_admin/inventory_alerts.html', context)


# ==================== QUẢN LÝ DANH MỤC ====================
@login_required(login_url='login')
@user_passes_test(is_admin, login_url='home')
def admin_categories(request):
    """Quản lý danh mục - List & Create"""
    from django.contrib import messages
    
    if request.method == 'POST':
        name = request.POST.get('name')
        slug = request.POST.get('slug') or None
        parent_id = request.POST.get('parent') or None
        description = request.POST.get('description', '')
        image = request.FILES.get('image')
        
        try:
            category = Category.objects.create(
                name=name,
                slug=slug,
                parent_id=parent_id if parent_id else None,
                description=description,
                image=image
            )
            messages.success(request, f'✓ Đã thêm danh mục "{category.name}"')
        except Exception as e:
            messages.error(request, f'✗ Lỗi: {str(e)}')
        
        return redirect('admin_categories')
    
    # GET: Hiển thị danh sách
    categories = Category.objects.all().order_by('parent__id', 'name')
    parents = Category.objects.filter(parent__isnull=True)
    
    # Đếm số sản phẩm cho mỗi category
    for cat in categories:
        cat.product_count = cat.product_set.count()
    
    context = {
        'categories': categories,
        'parents': parents,
    }
    return render(request, 'app/my_admin/categories.html', context)


@login_required(login_url='login')
@user_passes_test(is_admin, login_url='home')
def admin_category_edit(request, id):
    """Sửa danh mục"""
    from django.contrib import messages
    
    category = get_object_or_404(Category, id=id)
    
    if request.method == 'POST':
        category.name = request.POST.get('name')
        category.slug = request.POST.get('slug') or None
        parent_id = request.POST.get('parent') or None
        category.parent_id = parent_id if parent_id else None
        category.description = request.POST.get('description', '')
        
        if 'image' in request.FILES:
            category.image = request.FILES['image']
        
        try:
            category.save()
            messages.success(request, f'✓ Đã cập nhật danh mục "{category.name}"')
            return redirect('admin_categories')
        except Exception as e:
            messages.error(request, f'✗ Lỗi: {str(e)}')
    
    # Lấy danh sách parent (trừ chính nó và con của nó)
    parents = Category.objects.filter(parent__isnull=True).exclude(id=category.id)
    
    context = {
        'category': category,
        'parents': parents,
        'form': category,  # Pass category as form for template
    }
    return render(request, 'app/my_admin/categories_edit.html', context)


@login_required(login_url='login')
@user_passes_test(is_admin, login_url='home')
def admin_category_delete(request, id):
    """Xóa danh mục"""
    from django.contrib import messages
    
    category = get_object_or_404(Category, id=id)
    name = category.name
    
    try:
        category.delete()
        messages.success(request, f'✓ Đã xóa danh mục "{name}"')
    except Exception as e:
        messages.error(request, f'✗ Không thể xóa: {str(e)}')
    
    return redirect('admin_categories')


# ==================== QUẢN LÝ THƯƠNG HIỆU ====================
@login_required(login_url='login')
@user_passes_test(is_admin, login_url='home')
def admin_brands(request):
    """Quản lý thương hiệu - List & Create"""
    from django.contrib import messages
    
    if request.method == 'POST':
        name = request.POST.get('name')
        category_id = request.POST.get('category') or None
        origin = request.POST.get('origin', '')
        logo = request.FILES.get('logo')
        
        try:
            brand = Brand.objects.create(
                name=name,
                category_id=category_id if category_id else None,
                origin=origin,
                logo=logo
            )
            messages.success(request, f'✓ Đã thêm thương hiệu "{brand.name}"')
        except Exception as e:
            messages.error(request, f'✗ Lỗi: {str(e)}')
        
        return redirect('admin_brands')
    
    # GET: Hiển thị danh sách
    brands = Brand.objects.all().order_by('name')
    categories = Category.objects.filter(parent__isnull=True)
    
    context = {
        'brands': brands,
        'categories': categories,
    }
    return render(request, 'app/my_admin/brands.html', context)


@login_required(login_url='login')
@user_passes_test(is_admin, login_url='home')
def admin_brand_delete(request, id):
    """Xóa thương hiệu"""
    from django.contrib import messages
    
    brand = get_object_or_404(Brand, id=id)
    name = brand.name
    
    try:
        brand.delete()
        messages.success(request, f'✓ Đã xóa thương hiệu "{name}"')
    except Exception as e:
        messages.error(request, f'✗ Không thể xóa: {str(e)}')
    
    return redirect('admin_brands')


# ==================== QUẢN LÝ SPAM KEYWORDS ====================
@login_required(login_url='login')
@user_passes_test(is_admin, login_url='home')
def admin_spam_keywords(request):
    """Trang quản lý spam keywords"""
    from .models import SpamKeyword
    
    # Filter theo category nếu có
    category_filter = request.GET.get('category', '')
    
    if category_filter:
        keywords = SpamKeyword.objects.filter(category=category_filter).order_by('-severity', 'keyword')
    else:
        keywords = SpamKeyword.objects.all().order_by('-severity', 'keyword')
    
    # Stats
    total_keywords = SpamKeyword.objects.count()
    active_keywords = SpamKeyword.objects.filter(is_active=True).count()
    inactive_keywords = total_keywords - active_keywords
    
    context = {
        'keywords': keywords,
        'total_keywords': total_keywords,
        'active_keywords': active_keywords,
        'inactive_keywords': inactive_keywords,
    }
    return render(request, 'app/my_admin/spam_keywords.html', context)


@login_required(login_url='login')
@user_passes_test(is_admin, login_url='home')
def admin_spam_keywords_create(request):
    """Thêm spam keyword mới"""
    if request.method == 'POST':
        from .models import SpamKeyword
        
        keyword = request.POST.get('keyword', '').strip()
        category = request.POST.get('category', 'OTHER')
        severity = int(request.POST.get('severity', 100))
        description = request.POST.get('description', '').strip()
        is_active = request.POST.get('is_active') == 'on'
        
        if keyword:
            try:
                SpamKeyword.objects.create(
                    keyword=keyword,
                    category=category,
                    severity=severity,
                    description=description,
                    is_active=is_active
                )
                messages.success(request, f'✓ Đã thêm keyword "{keyword}"')
                
                # Clear cache
                from django.core.cache import cache
                cache.delete('spam_keywords_active')
            except Exception as e:
                messages.error(request, f'✗ Lỗi: {str(e)}')
        else:
            messages.error(request, '✗ Vui lòng nhập từ khóa')
    
    return redirect('admin_spam_keywords')


@login_required(login_url='login')
@user_passes_test(is_admin, login_url='home')
def admin_spam_keywords_edit(request, keyword_id):
    """Sửa spam keyword"""
    from .models import SpamKeyword
    
    keyword = get_object_or_404(SpamKeyword, id=keyword_id)
    
    if request.method == 'POST':
        keyword.keyword = request.POST.get('keyword', keyword.keyword).strip()
        keyword.category = request.POST.get('category', keyword.category)
        keyword.severity = int(request.POST.get('severity', keyword.severity))
        keyword.description = request.POST.get('description', '').strip()
        keyword.is_active = request.POST.get('is_active') == 'on'
        
        try:
            keyword.save()
            messages.success(request, f'✓ Đã cập nhật keyword "{keyword.keyword}"')
            
            # Clear cache
            from django.core.cache import cache
            cache.delete('spam_keywords_active')
        except Exception as e:
            messages.error(request, f'✗ Lỗi: {str(e)}')
        
        return redirect('admin_spam_keywords')
    
    context = {'keyword': keyword}
    return render(request, 'app/my_admin/spam_keyword_edit.html', context)


@login_required(login_url='login')
@user_passes_test(is_admin, login_url='home')
def admin_spam_keywords_toggle(request, keyword_id):
    """Bật/tắt spam keyword"""
    if request.method == 'POST':
        from .models import SpamKeyword
        
        keyword = get_object_or_404(SpamKeyword, id=keyword_id)
        keyword.is_active = not keyword.is_active
        keyword.save()
        
        status = "bật" if keyword.is_active else "tắt"
        messages.success(request, f'✓ Đã {status} keyword "{keyword.keyword}"')
        
        # Clear cache
        from django.core.cache import cache
        cache.delete('spam_keywords_active')
    
    return redirect('admin_spam_keywords')


@login_required(login_url='login')
@user_passes_test(is_admin, login_url='home')
def admin_spam_keywords_delete(request, keyword_id):
    """Xóa spam keyword"""
    if request.method == 'POST':
        from .models import SpamKeyword
        
        keyword = get_object_or_404(SpamKeyword, id=keyword_id)
        name = keyword.keyword
        
        try:
            keyword.delete()
            messages.success(request, f'✓ Đã xóa keyword "{name}"')
            
            # Clear cache
            from django.core.cache import cache
            cache.delete('spam_keywords_active')
        except Exception as e:
            messages.error(request, f'✗ Không thể xóa: {str(e)}')
    
    return redirect('admin_spam_keywords')