from config import Config
from dataset_handler import DatasetHandler
from data_processor import DataProcessor
from vector_store import VectorStore
from llm_service import LLMService
from bot_service import BotService
from telegram_interface import TelegramInterface
import logging
import asyncio

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        filename=Config.LOG_FILE,
        format=Config.LOG_FORMAT,
        level=Config.LOG_LEVEL
    )
    # Also log to console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(Config.LOG_FORMAT))
    logging.getLogger().addHandler(console_handler)

async def main():
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("Initializing bot components...")
        
        # Initialize dataset handler and load data
        dataset_handler = DatasetHandler()
        content = dataset_handler.load_dataset()
        qa_pairs = dataset_handler.extract_qa_pairs(content)
        
        # Get dataset statistics
        stats = dataset_handler.get_statistics()
        logger.info(f"Dataset statistics: {stats}")
        
        # Initialize data processor
        data_processor = DataProcessor()
        documents = data_processor.create_documents(qa_pairs)
        splits = data_processor.split_documents(documents)
        
        # Initialize vector store and add documents
        vector_store = VectorStore()
        vector_store.add_documents(splits)
        
        # Initialize LLM service
        llm_service = LLMService()
        
        # Initialize bot service
        bot_service = BotService(vector_store, llm_service)
        
        # Initialize and run telegram interface
        telegram_interface = TelegramInterface(bot_service)
        await telegram_interface.run()
        
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main())