from django import forms
from django.contrib.auth.models import User
from .models import CustomerProfile
from .models import Product

# Form Đăng Ký
class RegisterForm(forms.ModelForm):
    # Thêm các trường không có sẵn trong User model mặc định
    fullname = forms.CharField(label="Họ và tên", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nhập họ tên đầy đủ'}))
    email = forms.EmailField(label="Email", widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}))
    password = forms.CharField(label="Mật khẩu", widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Mật khẩu'}))
    confirm_password = forms.CharField(label="Nhập lại mật khẩu", widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Nhập lại mật khẩu'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        # 'username' là bắt buộc của Django, ta sẽ dùng nó làm tên đăng nhập
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tên đăng nhập'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("Mật khẩu nhập lại không khớp!")
        return cleaned_data

# Form Đăng Nhập (Đơn giản hóa từ AuthenticationForm)
class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tên đăng nhập'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Mật khẩu'}))


# app/forms.py

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__' # Hoặc liệt kê từng trường nếu muốn
        exclude = ['slug', 'sold_quantity', 'views', 'created_at'] # Loại bỏ các trường tự động
        
    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        # Thêm class CSS cho tất cả các ô input để dễ style
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-input'})    