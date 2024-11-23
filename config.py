from dotenv import load_dotenv
import os
import logging
from datetime import datetime
import sys

load_dotenv()

# Configure logging
def setup_logger():
    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # Create a new log file for each day
    log_filename = f"logs/bot_{datetime.now().strftime('%Y-%m-%d')}.log"
    
    # Configure logging format
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger('DecodeFXBot')

logger = setup_logger()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CUSTOMER_SERVICE_CONTACT = "0123456789"
DEFAULT_RESPONSE = (
    f"Xin lỗi, tôi không thể trả lời câu hỏi này. "
    f"Vui lòng liên hệ với bộ phận CSKH của chúng tôi tại: {CUSTOMER_SERVICE_CONTACT}"
)