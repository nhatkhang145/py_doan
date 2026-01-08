import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from transformers import pipeline
import logging

logger = logging.getLogger(__name__)

MODEL_NAME = "5CD-AI/Vietnamese-Sentiment-visobert"

# Biến toàn cục để lưu model (tránh load lại nhiều lần)
sentiment_pipeline = None

def load_model():
    """Hàm này tải model từ cache hoặc download"""
    global sentiment_pipeline
    if sentiment_pipeline is None:
        try:
            logger.info(f"Loading AI model: {MODEL_NAME}")
            #  Tải Tokenizer 
            tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
            #  Tải Model 
            model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
            #  Tạo Pipeline 
            sentiment_pipeline = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)
            logger.info("✓ Model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            sentiment_pipeline = None
    return sentiment_pipeline
            
            
def analyze_sentiment(text):
    """
    Hàm nhận nội dung bình luận -> Trả về (Label, Score)
    Label: 'POS', 'NEG', 'NEU'
    """
    global sentiment_pipeline
    
    # Kiểm tra text không rỗng
    if not text or not isinstance(text, str) or len(text.strip()) < 3:
        logger.warning(f"Text too short or invalid")
        return 'NEU', 50.0
    
    # Nếu chưa có model thì tải ngay
    if sentiment_pipeline is None:
        try:
            load_model()
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            return 'NEU', 50.0
    
    # Nếu load thất bại
    if sentiment_pipeline is None:
        logger.error("Model pipeline is still None after loading attempt")
        return 'NEU', 50.0
    
    # Cắt ngắn text nếu quá dài (AI chỉ đọc được tối đa 512 token)
    if len(text) > 512:
        text = text[:512]

    try:
        # Gọi AI phân tích
        result = sentiment_pipeline(text)[0]
        
        # Kết quả thô từ model thường là: LABEL_0 (NEG), LABEL_1 (POS), LABEL_2 (NEU)
        raw_label = result['label']
        score = round(result['score'] * 100, 2) # Đổi sang phần trăm (98.5%)

        logger.debug(f"AI result - raw_label: {raw_label}, score: {score}")

        # Chuyển đổi sang mã của chúng ta
        if raw_label in ['LABEL_1', 'POS']:
            return 'POS', score  # Tích cực
        elif raw_label in ['LABEL_0', 'NEG']:
            return 'NEG', score  # Tiêu cực
        elif raw_label in ['LABEL_2', 'NEU']:
            return 'NEU', score  # Trung tính
        else:
            return 'NEU', score  # Mặc định
            
    except Exception as e:
        logger.error(f"Error analyzing sentiment: {e}", exc_info=True)
        return 'NEU', 50.0