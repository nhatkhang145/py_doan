"""
Service xử lý reviews: spam detection, sentiment analysis
"""
import re
from django.core.cache import cache


def get_spam_keywords():
    """
    Lấy danh sách spam keywords từ database với caching
    Cache trong 5 phút để giảm query
    """
    cache_key = 'spam_keywords_active'
    keywords = cache.get(cache_key)
    
    if keywords is None:
        from app.models import SpamKeyword
        keywords = list(
            SpamKeyword.objects.filter(is_active=True)
            .values('keyword', 'severity', 'category')
            .order_by('-severity')
        )
        cache.set(cache_key, keywords, 300)  # Cache 5 phút
    
    return keywords


def detect_spam_keywords(comment):
    """
    Kiểm tra comment có chứa spam keywords không
    Return: (is_spam: bool, spam_keyword: str, severity: int, category: str)
    """
    comment_lower = comment.lower().strip()
    
    # Lấy keywords từ database
    spam_keywords = get_spam_keywords()
    
    # Kiểm tra từng keyword
    for item in spam_keywords:
        keyword = item['keyword'].lower()
        if keyword in comment_lower:
            return True, item['keyword'], item['severity'], item['category']
    
    # Kiểm tra lặp lại từ (VD: "tuyệt vời tuyệt vời tuyệt vời")
    words = comment_lower.split()
    if len(words) >= 2:  # Cần ít nhất 2 từ để check lặp
        word_counts = {}
        for word in words:
            if len(word) > 2:  # Chỉ đếm từ dài hơn 2 ký tự
                word_counts[word] = word_counts.get(word, 0) + 1
        
        # Nếu có từ lặp lại >= 3 lần
        for word, count in word_counts.items():
            if count >= 3:
                return True, f"Lặp từ: {word}", 90, "REPEAT"
    
    # Kiểm tra ký tự đặc biệt quá nhiều (> 30%)
    special_chars = re.findall(r'[!@#$%^&*()_+=\[\]{};:"\\|,.<>?/~`]', comment)
    if len(comment) > 5 and len(special_chars) > len(comment) * 0.3:
        return True, "Quá nhiều ký tự đặc biệt", 70, "OTHER"
    
    # Kiểm tra chữ IN HOA quá nhiều (> 80%)
    if len(comment) > 5:
        uppercase_count = sum(1 for c in comment if c.isupper())
        if uppercase_count > len(comment) * 0.8:
            return True, "Viết hoa quá nhiều", 60, "OTHER"
    
    return False, None, 0, None


def is_review_spam(comment, rating=None):
    
    is_spam, keyword, severity, category = detect_spam_keywords(comment)
    
    # Nếu tìm thấy spam keyword
    if is_spam:
        confidence = severity  # Sử dụng severity từ database
        
        # Nếu là 5 sao + spam keywords = tăng độ tin cậy
        if rating == 5 and severity >= 80:
            confidence = min(100, severity + 10)  # Tăng thêm 10%, tối đa 100
            reason = f"5 sao + spam keyword: '{keyword}'"
        else:
            reason = f"Chứa spam: '{keyword}'"
        
        return {
            'is_spam': True,
            'reason': reason,
            'confidence': confidence,
            'category': category or 'OTHER'
        }
    
    # Không phải spam
    return {
        'is_spam': False,
        'reason': '',
        'confidence': 0.0,
        'category': None
    }
