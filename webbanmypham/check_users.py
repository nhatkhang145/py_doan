import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'webbanmypham.settings')
django.setup()

from django.contrib.auth.models import User
from app.models import CustomerProfile

users = User.objects.all()
print('=== DANH SÁCH USER VÀ PROFILE ===\n')
for u in users:
    has_profile = hasattr(u, 'profile')
    print(f'User: {u.username}')
    print(f'  - is_superuser: {u.is_superuser}')
    print(f'  - has_profile: {has_profile}')
    if has_profile:
        print(f'  - role: {u.profile.role} ({u.profile.get_role_display()})')
    print()

# Kiểm tra xem có user nào là superuser không có profile
print('=== SUPERUSER KHÔNG CÓ PROFILE ===')
for u in User.objects.filter(is_superuser=True):
    if not hasattr(u, 'profile'):
        print(f'⚠️ Superuser {u.username} KHÔNG có CustomerProfile!')
