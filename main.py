import asyncio
import logging
from bot_service import BotService
from telegram_interface import TelegramInterface
from logger_config import LoggerSetup

async def main():
    """Main application entry point"""
    try:
        # Setup logging
        logger = LoggerSetup.setup()
        logger.info("Starting Decode FX Bot...")

        # Initialize services
        bot_service = BotService()
        telegram_interface = TelegramInterface(bot_service)
        
        # Run the bot
        await telegram_interface.run()

    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
