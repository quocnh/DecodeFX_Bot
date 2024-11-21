# telegram_interface.py
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
import logging
from config import Config

class TelegramInterface:
    def __init__(self, bot_service):
        self.logger = logging.getLogger(__name__)
        self.bot_service = bot_service
        self.application = Application.builder().token(Config.TELEGRAM_BOT_TOKEN).build()
        self.setup_handlers()

    def setup_handlers(self):
        """Setup message handlers"""
        try:
            # Basic commands
            self.application.add_handler(CommandHandler("start", self.start))
            self.application.add_handler(CommandHandler("help", self.help))
            
            # Handle private messages
            self.application.add_handler(
                MessageHandler(
                    filters.TEXT & filters.PRIVATE & ~filters.COMMAND,
                    self.handle_private_message
                )
            )
            
            # Handle group messages
            self.application.add_handler(
                MessageHandler(
                    filters.TEXT & filters.ChatType.GROUPS & ~filters.COMMAND,
                    self.handle_group_message
                )
            )
            
            self.logger.info("Telegram handlers set up successfully")
        except Exception as e:
            self.logger.error(f"Error setting up handlers: {str(e)}")
            raise

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        welcome_message = """
        Chào mừng bạn đến với Decode FX Support! 👋
        
        Tôi có thể giúp bạn với:
        • Thông tin KYC
        • Nạp/rút tiền
        • Vấn đề giao dịch
        • Hỗ trợ kỹ thuật
        """
        await update.message.reply_text(welcome_message)

    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_message = """
        📌 Cách sử dụng bot:
        
        Trong group chat:
        • Tag bot: @decodefx_bot + câu hỏi
        • Reply tin nhắn của bot
        
        Trong private chat:
        • Gửi câu hỏi trực tiếp
        
        ⚠️ Giờ làm việc: 24/7
        Hotline: XXXX
        """
        await update.message.reply_text(help_message)

    async def handle_private_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle messages in private chat"""
        try:
            message = update.message
            user = update.effective_user
            
            # Log incoming message
            self.logger.info(f"Private message from {user.username or user.id}: {message.text}")
            
            # Get response from bot service
            response, confidence = self.bot_service.get_response(
                message.text,
                str(user.id),
                user.username or "Unknown"
            )
            
            # Send response
            await message.reply_text(self.bot_service.prepare_response(response))
            
        except Exception as e:
            self.logger.error(f"Error in private message handler: {str(e)}")
            await message.reply_text(Config.DEFAULT_RESPONSE)

    async def handle_group_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle messages in groups"""
        try:
            message = update.message
            user = update.effective_user
            
            # Check if message mentions or replies to bot
            bot_username = (await context.bot.get_me()).username
            bot_mentioned = f"@{bot_username}" in message.text if message.text else False
            bot_replied = message.reply_to_message and message.reply_to_message.from_user.id == context.bot.id
            
            if not (bot_mentioned or bot_replied):
                return

            # Extract query
            query = message.text
            if bot_mentioned:
                # Remove bot username from query
                query = query.replace(f"@{bot_username}", "").strip()

            # Log group message
            self.logger.info(f"Group message from {user.username or user.id} in {message.chat.title}: {query}")
            
            # Get response from bot service
            response, confidence = self.bot_service.get_response(
                query,
                str(user.id),
                user.username or "Unknown"
            )
            
            # Send response
            await message.reply_text(
                text=self.bot_service.prepare_response(response),
                reply_to_message_id=message.message_id
            )
            
        except Exception as e:
            self.logger.error(f"Error in group message handler: {str(e)}")
            await message.reply_text(Config.DEFAULT_RESPONSE)

    async def run(self):
        """Run the bot"""
        try:
            self.logger.info("Starting bot...")
            await self.application.initialize()
            await self.application.start()
            await self.application.run_polling(drop_pending_updates=True)
        except Exception as e:
            self.logger.error(f"Error running bot: {str(e)}")
            raise
