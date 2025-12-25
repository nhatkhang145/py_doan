from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from .forms import RegisterForm, LoginForm
from .models import CustomerProfile, Product, Category, Order, Brand
from .cart import Cart 
from .forms import ProductForm

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

# --- CỬA HÀNG (SHOP) ---
def shop(request):
    product_list = Product.objects.all().order_by('-id')
    categories = Category.objects.all()
    
    paginator = Paginator(product_list, 12) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'categories': categories
    }
    return render(request, 'app/shop.html', context)

# --- CHI TIẾT SẢN PHẨM (Đã xóa bản sao thừa) ---
def product_detail(request, id):
    product = get_object_or_404(Product, id=id)
    # Lấy 4 sản phẩm cùng danh mục
    related_products = Product.objects.filter(category=product.category).exclude(id=id)[:4]
    
    context = {'product': product, 'related_products': related_products}
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
def cart_detail(request):
    cart = Cart(request)
    return render(request, 'app/cart.html', {'cart': cart})

# --- LOGIC ADMIN (Check quyền) ---
def is_admin(user):
    try:
        return user.is_superuser or user.profile.role in [1, 2]
    except:
        return False

# 1. TRANG DASHBOARD (TỔNG QUAN)
@login_required(login_url='login')
@user_passes_test(is_admin, login_url='home')
def admin_dashboard(request):
    # Thống kê cơ bản
    customer_count = CustomerProfile.objects.count()
    product_count = Product.objects.count()
    order_count = Order.objects.count()
    
    # Gửi dữ liệu sang template
    context = {
        'customer_count': customer_count,
        'product_count': product_count,
        'order_count': order_count
    }
    return render(request, 'app/my_admin/dashboard.html', context)

# 2. TRANG QUẢN LÝ KHÁCH HÀNG
@login_required(login_url='login')
@user_passes_test(is_admin, login_url='home')
def admin_customers(request):
    customers = CustomerProfile.objects.all()
    context = {'customers': customers}
    return render(request, 'app/my_admin/customers.html', context)

# 3. TRANG QUẢN LÝ SẢN PHẨM
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

# 4. THÊM SẢN PHẨM
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

# 5. SỬA SẢN PHẨM
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