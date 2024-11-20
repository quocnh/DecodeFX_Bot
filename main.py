import os
import asyncio
from decode_customer_service_bot import DecodeCustomerServiceBot
from telegram_interface import TelegramInterface
from dotenv import load_dotenv

def main():
    # Load environment variables
    load_dotenv()
    
    # Get tokens from environment variables
    huggingface_token = os.getenv('HUGGINGFACE_TOKEN')
    telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not huggingface_token or not telegram_token:
        raise ValueError("Missing required environment variables. Please check .env file")
    
    # Initialize the customer service bot
    bot = DecodeCustomerServiceBot(huggingface_token)
    
    # Load and process training data
    with open('dataset/decode-fx-vietnamese-dataset.md', 'r', encoding='utf-8') as f:
        markdown_content = f.read()
    
    qa_pairs = bot.process_training_data(markdown_content)
    bot.train(qa_pairs)
 

    # Initialize and start Telegram interface
    telegram_interface = TelegramInterface(bot, telegram_token)
    
    # Run the bot
    asyncio.run(telegram_interface.application.run_polling(drop_pending_updates=True))

if __name__ == "__main__":
    main()