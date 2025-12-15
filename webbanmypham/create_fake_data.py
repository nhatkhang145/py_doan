import os
import django
import random
from django.utils.text import slugify
from decimal import Decimal
from datetime import date

# 1. Thiết lập môi trường Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'webbanmypham.settings')
django.setup()

from app.models import Category, Brand, Product, ProductBatch

def create_data():
    print("🚀 Đang khởi tạo dữ liệu mẫu...")

    # --- 1. TẠO DANH MỤC (CATEGORY) ---
    categories = ['Son môi', 'Chăm sóc da', 'Trang điểm mặt', 'Nước hoa']
    db_cats = []
    for name in categories:
        # get_or_create: Nếu có rồi thì lấy, chưa có thì tạo mới (tránh trùng)
        cat, created = Category.objects.get_or_create(
            name=name, 
            defaults={'slug': slugify(name, allow_unicode=True)}
        )
        db_cats.append(cat)
    print(f"✅ Đã tạo {len(db_cats)} Danh mục")

    # --- 2. TẠO THƯƠNG HIỆU (BRAND) ---
    brands = ['L\'Oreal', 'Maybelline', 'Innisfree', 'MAC', 'Dior']
    db_brands = []
    for name in brands:
        brand, created = Brand.objects.get_or_create(
            name=name,
            defaults={'origin': 'Pháp/Hàn', 'slug': slugify(name, allow_unicode=True)}
        )
        db_brands.append(brand)
    print(f"✅ Đã tạo {len(db_brands)} Thương hiệu")

    # --- 3. TẠO SẢN PHẨM (PRODUCT) ---
    # Xóa sản phẩm cũ để tránh rác (Tùy chọn)
    # Product.objects.all().delete()
    
    product_names = [
        "Son Kem Lì Black Rouge", "Kem Nền Fit Me", "Phấn Nước Laneige", 
        "Tẩy Trang Bioderma", "Sữa Rửa Mặt CeraVe", "Toner Klairs",
        "Serum Vitamin C", "Kem Dưỡng Ẩm Neutrogena", "Son Dưỡng Dior", "Mascara Kiss Me"
    ]

    for i, name in enumerate(product_names):
        # Chọn ngẫu nhiên danh mục và thương hiệu
        cat = random.choice(db_cats)
        brand = random.choice(db_brands)
        price = random.randint(150, 2000) * 1000 # Giá từ 150k đến 2tr

        product, created = Product.objects.get_or_create(
            name=name,
            defaults={
                'slug': slugify(name, allow_unicode=True) + f"-{i}", # Thêm số để tránh trùng slug
                'sku': f"SKU-{random.randint(10000, 99999)}",
                'category': cat,
                'brand': brand,
                'price': price,
                'sale_price': price * 0.9 if random.choice([True, False]) else 0, # 50% cơ hội giảm giá
                'stock_quantity': 100,
                'image': 'products/default_product.jpg', # Đảm bảo bạn có ảnh này hoặc để trống
                'description': f"Mô tả chi tiết cho sản phẩm {name}. Hàng chính hãng 100%.",
                'target_skin_type': random.choice(['Da dầu', 'Da khô', 'Mọi loại da'])
            }
        )
        
        # --- 4. TẠO LÔ HÀNG (BATCH) CHO SẢN PHẨM ĐÓ ---
        ProductBatch.objects.create(
            product=product,
            batch_code=f"LOHANG-{random.randint(100,999)}",
            quantity=50,
            manufacturing_date=date(2023, 1, 1),
            expiry_date=date(2026, 1, 1),
            import_price=price * 0.7
        )

    print(f"✅ Đã tạo 10 Sản phẩm & Lô hàng")
    print("🎉 HOÀN TẤT! Website của bạn đã có dữ liệu.")

if __name__ == '__main__':
    create_data()