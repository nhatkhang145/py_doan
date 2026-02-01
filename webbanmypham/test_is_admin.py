import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'webbanmypham.settings')
django.setup()

from django.contrib.auth.models import User
from app.views import is_admin

admin_user = User.objects.get(username='admin')
print(f'User: {admin_user.username}')
print(f'is_superuser: {admin_user.is_superuser}')
print(f'profile.role: {admin_user.profile.role}')
print(f'\nis_admin() result: {is_admin(admin_user)}')

# Test với user thường
user1 = User.objects.get(username='user1')
print(f'\nUser: {user1.username}')
print(f'is_superuser: {user1.is_superuser}')
print(f'profile.role: {user1.profile.role}')
print(f'is_admin() result: {is_admin(user1)}')
