import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Bot Configuration
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    CONFIDENCE_THRESHOLD = 0.75
    
    # Paths
    DATASET_PATH = "data/dataset.md"
    LOG_FILE = "logs/bot.log"
    
    # Default Response
    DEFAULT_RESPONSE = """
    Xin lỗi, tôi chưa hiểu rõ câu hỏi của bạn.
    Vui lòng thử:
    1. Đặt lại câu hỏi rõ ràng hơn
    2. Liên hệ hotline: XXXX
    3. Email: support@decodefx.com
    """
    
    MODERATE_CONFIDENCE_SUFFIX = "\n\nNếu cần thêm thông tin, vui lòng liên hệ hotline: XXXX"
    
    # General chat patterns
    GENERAL_PATTERNS = [
        {
            'patterns': [r'(chào|hello|hi|hey)', r'(có ai|ai đó)'],
            'response': """
            Chào bạn! Mình là bot hỗ trợ của Decode FX. 
            Mình có thể giúp bạn về:
            • Mở tài khoản và KYC
            • Nạp/rút tiền
            • Vấn đề giao dịch
            • Hỗ trợ kỹ thuật
            """
        },
        {
            'patterns': [r'(cảm ơn|thank|tks|thanks)'],
            'response': "Cảm ơn bạn đã liên hệ Decode FX! 😊"
        }
    ]
