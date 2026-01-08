"""
Script để seed spam keywords mẫu vào database
Chạy: python scripts/seed_spam_keywords.py
"""

import os
import sys
import django

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'webbanmypham.settings')
django.setup()

from app.models import SpamKeyword

# Danh sách spam keywords mẫu
SPAM_DATA = [
    # FINANCE - Tài chính
    {'keyword': 'vay vốn', 'category': 'FINANCE', 'severity': 100, 'description': 'Quảng cáo cho vay'},
    {'keyword': 'vay tiền', 'category': 'FINANCE', 'severity': 100, 'description': 'Quảng cáo cho vay'},
    {'keyword': 'cho vay', 'category': 'FINANCE', 'severity': 100, 'description': 'Quảng cáo cho vay'},
    {'keyword': 'lãi suất', 'category': 'FINANCE', 'severity': 95, 'description': 'Liên quan đến tài chính'},
    {'keyword': 'đầu tư', 'category': 'FINANCE', 'severity': 90, 'description': 'Mời đầu tư'},
    {'keyword': 'kiếm tiền', 'category': 'FINANCE', 'severity': 90, 'description': 'Mời kiếm tiền'},
    {'keyword': 'làm giàu', 'category': 'FINANCE', 'severity': 95, 'description': 'Lừa đảo làm giàu'},
    
    # CONTACT - Liên hệ/Quảng cáo
    {'keyword': 'liên hệ zalo', 'category': 'CONTACT', 'severity': 100, 'description': 'Mời liên hệ ngoài'},
    {'keyword': 'zalo', 'category': 'CONTACT', 'severity': 85, 'description': 'Đề cập Zalo'},
    {'keyword': 'liên hệ sdt', 'category': 'CONTACT', 'severity': 95, 'description': 'Mời gọi điện'},
    {'keyword': 'inbox', 'category': 'CONTACT', 'severity': 80, 'description': 'Mời nhắn tin riêng'},
    {'keyword': 'quảng cáo', 'category': 'CONTACT', 'severity': 100, 'description': 'Quảng cáo trực tiếp'},
    {'keyword': 'cần bán', 'category': 'CONTACT', 'severity': 95, 'description': 'Bán hàng trong review'},
    {'keyword': 'cần mua', 'category': 'CONTACT', 'severity': 90, 'description': 'Mua bán trong review'},
    
    # EXTERNAL - Link bên ngoài
    {'keyword': 'facebook', 'category': 'EXTERNAL', 'severity': 90, 'description': 'Đề cập Facebook'},
    {'keyword': 'fb.com', 'category': 'EXTERNAL', 'severity': 100, 'description': 'Link Facebook'},
    {'keyword': '.com', 'category': 'EXTERNAL', 'severity': 85, 'description': 'Link website'},
    {'keyword': 'http', 'category': 'EXTERNAL', 'severity': 100, 'description': 'Link URL'},
    {'keyword': 'www.', 'category': 'EXTERNAL', 'severity': 100, 'description': 'Link website'},
    {'keyword': 'shopee', 'category': 'EXTERNAL', 'severity': 80, 'description': 'Chuyển hướng sang sàn khác'},
    {'keyword': 'lazada', 'category': 'EXTERNAL', 'severity': 80, 'description': 'Chuyển hướng sang sàn khác'},
    
    # FAKE - Hàng giả
    {'keyword': 'shop khác', 'category': 'FAKE', 'severity': 90, 'description': 'Đề cập shop khác'},
    {'keyword': 'hàng fake', 'category': 'FAKE', 'severity': 100, 'description': 'Cáo buộc hàng giả'},
    {'keyword': 'fake', 'category': 'FAKE', 'severity': 95, 'description': 'Cáo buộc hàng giả'},
    {'keyword': 'nhái', 'category': 'FAKE', 'severity': 95, 'description': 'Cáo buộc hàng nhái'},
    {'keyword': 'hàng nhái', 'category': 'FAKE', 'severity': 100, 'description': 'Cáo buộc hàng nhái'},
    
    # REPEAT - Spam lặp từ
    {'keyword': 'tuyệt vời tuyệt vời', 'category': 'REPEAT', 'severity': 90, 'description': 'Lặp từ spam'},
    {'keyword': 'rất tốt rất tốt', 'category': 'REPEAT', 'severity': 85, 'description': 'Lặp từ spam'},
    
    # OTHER - Khác
    {'keyword': 'freeship', 'category': 'OTHER', 'severity': 70, 'description': 'Quảng cáo freeship'},
    {'keyword': 'mua ngay', 'category': 'OTHER', 'severity': 75, 'description': 'Call to action'},
    {'keyword': 'đặc biệt', 'category': 'OTHER', 'severity': 60, 'description': 'Khuyến mãi đặc biệt'},
    {'keyword': 'spam', 'category': 'OTHER', 'severity': 100, 'description': 'Spam trực tiếp'},
]

def seed_spam_keywords():
    """Import spam keywords vào database"""
    print("🚀 Starting spam keywords seeding...")
    
    created_count = 0
    updated_count = 0
    
    for data in SPAM_DATA:
        keyword, created = SpamKeyword.objects.get_or_create(
            keyword=data['keyword'],
            defaults={
                'category': data['category'],
                'severity': data['severity'],
                'description': data['description'],
                'is_active': True
            }
        )
        
        if created:
            created_count += 1
            print(f"  ✓ Created: {keyword.keyword} ({keyword.category})")
        else:
            # Update existing
            keyword.category = data['category']
            keyword.severity = data['severity']
            keyword.description = data['description']
            keyword.save()
            updated_count += 1
            print(f"  ↻ Updated: {keyword.keyword}")
    
    print(f"\n✅ Seeding complete!")
    print(f"   - Created: {created_count} keywords")
    print(f"   - Updated: {updated_count} keywords")
    print(f"   - Total: {SpamKeyword.objects.count()} keywords in database")

if __name__ == '__main__':
    seed_spam_keywords()
