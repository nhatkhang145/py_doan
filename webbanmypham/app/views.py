from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .forms import RegisterForm, LoginForm
from .models import CustomerProfile

# --- Giữ nguyên hàm home cũ ---
def home(request):
    return render(request, 'app/home.html')

# 1. View Đăng Ký
def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            # Bước 1: Lưu User (bảng auth_user)
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()

            # Bước 2: Tạo CustomerProfile (bảng app_customerprofile)
            CustomerProfile.objects.create(
                user=user,
                fullname=form.cleaned_data['fullname'],
                # skin_type mặc định là 'unknown' như trong models.py
            )
            
            messages.success(request, "Đăng ký thành công! Hãy đăng nhập.")
            return redirect('login')
        else:
            messages.error(request, "Đăng ký thất bại. Vui lòng kiểm tra lại thông tin.")
    else:
        form = RegisterForm()
    
    return render(request, 'app/register.html', {'form': form})

# 2. View Đăng Nhập
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                
                # --- PHẦN CODE MỚI: PHÂN QUYỀN ---
                
                # 1. Ưu tiên: Nếu đang đi link nào đó bị bắt đăng nhập (VD: checkout) -> Trả về link đó
                next_url = request.GET.get('next')
                if next_url:
                    return redirect(next_url)

                # 2. Nếu đăng nhập chủ động -> Kiểm tra Role để điều hướng
                try:
                    # Lấy thông tin role từ CustomerProfile
                    # Lưu ý: user.profile hoạt động nhờ related_name='profile' trong models.py
                    user_role = user.profile.role 
                    
                    if user_role == 1: # Là Admin
                        return redirect('/admin/') # Chuyển thẳng vào trang Admin của Django
                        # Hoặc: return redirect('dashboard') # Nếu bạn làm trang Dashboard riêng
                        
                    elif user_role == 2: # Là Nhân viên
                        return redirect('/admin/') # Tạm thời cho vào Admin hoặc trang xử lý đơn riêng
                        
                    else: # Là Khách hàng (role == 0)
                        return redirect('home') # Về trang chủ mua sắm
                        
                except Exception as e:
                    # Trường hợp User này chưa có Profile (VD: superuser tạo bằng lệnh terminal cũ)
                    if user.is_superuser:
                        return redirect('/admin/')
                    return redirect('home')
                
            else:
                messages.error(request, "Sai tên đăng nhập hoặc mật khẩu!")
    else:
        form = LoginForm()
        
    return render(request, 'app/login.html', {'form': form})

# 3. View Đăng Xuất
def logout_view(request):
    logout(request)
    return redirect('home')