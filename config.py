import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

class Config:
    # Base paths
    BASE_DIR = Path(__file__).resolve().parent.parent
    DATASET_DIR = BASE_DIR / "dataset"
    LOG_DIR = BASE_DIR / "logs"
    
    # Create directories if they don't exist
    LOG_DIR.mkdir(exist_ok=True)
    
    # API Keys
    HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN")
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    
    # Model configs
    EMBEDDING_MODEL = "vinai/phobert-base"
    LLM_MODEL = "meta-llama/Llama-2-7b-chat-hf"
    
    # Vector store configs
    CHROMA_PERSIST_DIR = str(BASE_DIR / "chroma_db")
    COLLECTION_NAME = "decode_fx_qa"
    
    # Chunking configs
    CHUNK_SIZE = 500
    CHUNK_OVERLAP = 50
    
    # Similarity threshold
    SIMILARITY_THRESHOLD = 0.7
    
    # Dataset
    DATASET_PATH = str(DATASET_DIR / "decode-fx-vietnamese-dataset.md")
    
    # Logging
    LOG_FILE = str(LOG_DIR / "bot.log")
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOG_LEVEL = 'INFO'
    
    # Prompt templates
    SYSTEM_PROMPT = """Bạn là trợ lý AI đa năng của Decode FX.
    Hãy trả lời câu hỏi một cách chuyên nghiệp.
    Với câu hỏi về Decode FX, hãy cung cấp thông tin chính xác.
    Với câu hỏi chung, hãy trả lời dựa trên kiến thức của bạn."""