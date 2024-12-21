import os
import sys

# Add the project root directory to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

from models.enhanced_bot_model import EnhancedBotModel  # Make sure this path matches your file structure
from interfaces.telegram_interface import TelegramInterface
from config import logger

def main():
    try:
        logger.info("Starting DecodeFX Bot with Enhanced Reasoning")
        
        # Initialize the enhanced bot model with your dataset
        dataset_path = os.path.join(project_root, 'data', 'decode-fx-vietnamese-dataset.md')
        logger.info("Initializing enhanced bot model...")
        bot_model = EnhancedBotModel(dataset_path)
        
        # Initialize and run the Telegram interface
        logger.info("Initializing Telegram interface...")
        telegram_interface = TelegramInterface(bot_model)
        
        logger.info("Enhanced Bot is ready to serve!")
        telegram_interface.run()
        
    except Exception as e:
        logger.critical(f"Critical error in main: {str(e)}")
        raise

if __name__ == "__main__":
    main()