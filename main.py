import asyncio
import logging
from bot_service import BotService
from telegram_interface import TelegramInterface
from logger_config import LoggerSetup

def handle_exception(loop, context):
    msg = context.get("exception", context["message"])
    logging.error(f"Caught exception: {msg}")

async def main():
    # Setup logging
    logger = LoggerSetup.setup()
    logger.info("Starting Decode FX Bot...")

    # Get event loop
    loop = asyncio.get_event_loop()
    loop.set_exception_handler(handle_exception)
    
    try:
        # Initialize services
        bot_service = BotService()
        telegram_interface = TelegramInterface(bot_service)
        
        # Run the bot
        await telegram_interface.run_polling()
        
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    except Exception as e:
        logger.error(f"Bot error: {str(e)}")
    finally:
        logger.info("Bot shutdown complete")

if __name__ == "__main__":
    try:
        # Run with new event loop
        policy = asyncio.get_event_loop_policy()
        policy.set_event_loop(policy.new_event_loop())
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nBot stopped by user")
    except Exception as e:
        print(f"Fatal error: {str(e)}")
