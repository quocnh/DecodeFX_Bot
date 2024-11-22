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
            self.application.add_handler(CommandHandler("start", self.command_start))
            self.application.add_handler(CommandHandler("help", self.command_help))
            
            # Handle messages
            self.application.add_handler(
                MessageHandler(
                    (filters.TEXT & ~filters.COMMAND & 
                     (filters.ChatType.GROUPS | filters.ChatType.PRIVATE)),
                    self.handle_message
                )
            )
            
            self.logger.info("Telegram handlers set up successfully")
        except Exception as e:
            self.logger.error(f"Error setting up handlers: {str(e)}")
            raise

    def get_user_info(self, user) -> str:
        """Get user info string"""
        if user.username:
            return f"{user.username} ({user.id})"
        return f"User {user.id}"

    async def command_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        try:
            user = update.effective_user
            user_info = self.get_user_info(user)
            
            welcome_message = """
            Chào mừng bạn đến với Decode FX Support! 👋
            
            Tôi có thể giúp bạn với:
            • Thông tin KYC
            • Nạp/rút tiền
            • Vấn đề giao dịch
            • Hỗ trợ kỹ thuật
            
            Gõ /help để xem hướng dẫn sử dụng.
            """
            await update.message.reply_text(welcome_message)
            self.logger.info(f"Start command from {user_info}")
        except Exception as e:
            self.logger.error(f"Error in start command: {str(e)}")
            await update.message.reply_text("Xin lỗi, có lỗi xảy ra. Vui lòng thử lại sau.")

    async def command_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        try:
            user = update.effective_user
            user_info = self.get_user_info(user)
            
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
            self.logger.info(f"Help command from {user_info}")
        except Exception as e:
            self.logger.error(f"Error in help command: {str(e)}")
            await update.message.reply_text("Xin lỗi, có lỗi xảy ra. Vui lòng thử lại sau.")

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle messages in both private chats and groups"""
        try:
            message = update.message
            user = update.effective_user
            chat_type = message.chat.type
            chat_id = message.chat_id
            query = message.text
            
            user_info = self.get_user_info(user)
            self.logger.info(f"Message from {user_info} in {chat_type} chat {chat_id}: {query}")

            # Handle group messages
            if chat_type in ['group', 'supergroup']:
                bot_username = (await context.bot.get_me()).username
                bot_mentioned = f"@{bot_username}" in query
                bot_replied = message.reply_to_message and message.reply_to_message.from_user.id == context.bot.id
                
                if not (bot_mentioned or bot_replied):
                    return
                
                if bot_mentioned:
                    query = query.replace(f"@{bot_username}", "").strip()

            # Get response from bot service
            response, confidence = self.bot_service.get_response(
                query,
                str(user.id),
                user.username or user_info
            )

            # Send response
            await message.reply_text(
                self.bot_service.prepare_response(response),
                reply_to_message_id=message.message_id
            )

        except Exception as e:
            self.logger.error(f"Error handling message: {str(e)}")
            await message.reply_text(Config.DEFAULT_RESPONSE)

    async def run(self):
        """Run the bot"""
        self.logger.info("Bot is starting...")
        async with self.application:
            self.logger.info("Bot is running...")
            await self.application.run_polling(allowed_updates=Update.ALL_TYPES)

    async def run_polling(self):
        """Run the bot with polling"""
        self.logger.info("Bot is starting...")
        await self.application.initialize()
        await self.application.start()
        self.logger.info("Bot is running...")
        await self.application.run_polling(allowed_updates=Update.ALL_TYPES)
