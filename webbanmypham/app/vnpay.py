"""
VNPay Payment Integration
Tích hợp thanh toán VNPay cho Beauty Shop
"""
import hashlib
import hmac
import urllib.parse
from datetime import datetime


class VNPayConfig:
    """Cấu hình VNPay"""
    
    # Thông tin từ VNPay Sandbox
    VNPAY_TMN_CODE = "APZK1ED9"
    VNPAY_HASH_SECRET = "LRJCRIXGYBLLGENPRTSDG4ZN6F7CVWXA"
    VNPAY_PAYMENT_URL = "https://sandbox.vnpayment.vn/paymentv2/vpcpay.html"
    VNPAY_API_URL = "https://sandbox.vnpayment.vn/merchant_webapi/api/transaction"


class VNPay:
    """Xử lý thanh toán VNPay"""
    
    def __init__(self):
        self.request_data = {}
        self.response_data = {}
    
    def build_payment_url(self, return_url, order_code, amount, order_desc, ip_address, bank_code=None):
        """Tạo URL thanh toán VNPay"""
        
        # Các tham số bắt buộc
        self.request_data = {
            'vnp_Version': '2.1.0',
            'vnp_Command': 'pay',
            'vnp_TmnCode': VNPayConfig.VNPAY_TMN_CODE,
            'vnp_Amount': str(int(amount) * 100),  # VNPay tính theo VNĐ * 100
            'vnp_CurrCode': 'VND',
            'vnp_TxnRef': order_code,
            'vnp_OrderInfo': order_desc,
            'vnp_OrderType': 'other',
            'vnp_Locale': 'vn',
            'vnp_ReturnUrl': return_url,
            'vnp_IpAddr': ip_address,
            'vnp_CreateDate': datetime.now().strftime('%Y%m%d%H%M%S'),
        }
        
        # Thêm mã ngân hàng nếu có
        if bank_code:
            self.request_data['vnp_BankCode'] = bank_code
        
        # Sắp xếp params theo alphabet
        sorted_params = sorted(self.request_data.items())
        query_string = urllib.parse.urlencode(sorted_params)
        
        # Tạo secure hash (HMAC SHA512)
        secure_hash = hmac.new(
            VNPayConfig.VNPAY_HASH_SECRET.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha512
        ).hexdigest()
        
        # Tạo URL đầy đủ
        payment_url = f"{VNPayConfig.VNPAY_PAYMENT_URL}?{query_string}&vnp_SecureHash={secure_hash}"
        
        return payment_url
    
    def validate_response(self, response_data):
        """Xác thực response từ VNPay"""
        
        # Lấy secure hash từ response
        vnp_secure_hash = response_data.get('vnp_SecureHash', '')
        
        # Bỏ vnp_SecureHash và vnp_SecureHashType khỏi data để tính toán
        input_data = {k: v for k, v in response_data.items() 
                      if k not in ['vnp_SecureHash', 'vnp_SecureHashType']}
        
        # Sắp xếp và encode
        sorted_params = sorted(input_data.items())
        query_string = urllib.parse.urlencode(sorted_params)
        
        # Tính hash
        calculated_hash = hmac.new(
            VNPayConfig.VNPAY_HASH_SECRET.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha512
        ).hexdigest()
        
        # So sánh hash (case-insensitive)
        return vnp_secure_hash.lower() == calculated_hash.lower()
    
    @staticmethod
    def get_response_message(response_code):
        """Lấy thông báo tương ứng với mã response"""
        messages = {
            '00': 'Giao dịch thành công',
            '07': 'Trừ tiền thành công. Giao dịch bị nghi ngờ (liên quan tới lừa đảo, giao dịch bất thường).',
            '09': 'Giao dịch không thành công do: Thẻ/Tài khoản của khách hàng chưa đăng ký dịch vụ InternetBanking tại ngân hàng.',
            '10': 'Giao dịch không thành công do: Khách hàng xác thực thông tin thẻ/tài khoản không đúng quá 3 lần',
            '11': 'Giao dịch không thành công do: Đã hết hạn chờ thanh toán. Xin quý khách vui lòng thực hiện lại giao dịch.',
            '12': 'Giao dịch không thành công do: Thẻ/Tài khoản của khách hàng bị khóa.',
            '13': 'Giao dịch không thành công do Quý khách nhập sai mật khẩu xác thực giao dịch (OTP). Xin quý khách vui lòng thực hiện lại giao dịch.',
            '24': 'Giao dịch không thành công do: Khách hàng hủy giao dịch',
            '51': 'Giao dịch không thành công do: Tài khoản của quý khách không đủ số dư để thực hiện giao dịch.',
            '65': 'Giao dịch không thành công do: Tài khoản của Quý khách đã vượt quá hạn mức giao dịch trong ngày.',
            '75': 'Ngân hàng thanh toán đang bảo trì.',
            '79': 'Giao dịch không thành công do: KH nhập sai mật khẩu thanh toán quá số lần quy định. Xin quý khách vui lòng thực hiện lại giao dịch',
            '99': 'Các lỗi khác (lỗi còn lại, không có trong danh sách mã lỗi đã liệt kê)',
        }
        return messages.get(response_code, 'Lỗi không xác định')


def get_client_ip(request):
    """Lấy IP của client"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR', '127.0.0.1')
    return ip
