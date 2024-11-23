import os
import sys

# Add the project root directory to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

from models.bot_llm import BotLLMModel
from interfaces.telegram_interface import TelegramInterface
from config import logger

def main():
    try:
        logger.info("Starting DecodeFX Bot")
        
        # Initialize the bot model with your dataset
        dataset_path = os.path.join(project_root, 'data', 'decode-fx-vietnamese-dataset.md')
        logger.info("Initializing bot model...")
        bot_model = BotLLMModel(dataset_path)
        
        # Initialize and run the Telegram interface
        logger.info("Initializing Telegram interface...")
        telegram_interface = TelegramInterface(bot_model)
        
        logger.info("Bot is ready to serve!")
        telegram_interface.run()
        
    except Exception as e:
        logger.critical(f"Critical error in main: {str(e)}")
        raise

if __name__ == "__main__":
    main()