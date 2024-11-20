from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from bot_service import BotService
import logging
from config import Config

class TelegramInterface:
    def __init__(self, bot_service: BotService, token: str = Config.TELEGRAM_BOT_TOKEN):
        self.logger = logging.getLogger(__name__)
        self.bot_service = bot_service
        self.application = Application.builder().token(token).build()
        self.setup_handlers()

    def setup_handlers(self):
        """Setup message handlers"""
        try:
            self.application.add_handler(CommandHandler("start", self.start))
            self.application.add_handler(CommandHandler("help", self.help))
            self.application.add_handler(
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    self.handle_message
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
        
        Gõ /help để xem thêm thông tin.
        """
        await update.message.reply_text(welcome_message)
        self.logger.info(f"Start command from user {update.effective_user.id}")

    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_message = """
        📌 Cách sử dụng bot:
        1. Đặt câu hỏi trực tiếp
        2. Sử dụng ngôn ngữ đơn giản và rõ ràng
        3. Mỗi tin nhắn chỉ nên hỏi một vấn đề
        
        ⚠️ Lưu ý:
        • Trong giờ làm việc sẽ có nhân viên CSKH hỗ trợ
        • Ngoài giờ bot sẽ tự động trả lời
        • Vấn đề khẩn cấp vui lòng gọi hotline
        """
        await update.message.reply_text(help_message)
        self.logger.info(f"Help command from user {update.effective_user.id}")

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle incoming messages"""
        try:
            query = update.message.text
            chat_id = update.message.chat_id
            user_id = update.effective_user.id
            
            self.logger.info(f"Message from user {user_id} in chat {chat_id}: {query}")
            
            response, confidence = self.bot_service.get_response(query)
            response = self.bot_service.prepare_response(response)
            
            if response:
                self.logger.info(f"Sending response with confidence {confidence}")
                await update.message.reply_text(response)
            else:
                self.logger.warning("No response generated")
                await update.message.reply_text("""
                Xin lỗi, đã có lỗi xảy ra.
                Vui lòng thử lại sau hoặc liên hệ support@decode.com
                """)
                
        except Exception as e:
            self.logger.error(f"Error handling message: {str(e)}")
            await update.message.reply_text("""
            Xin lỗi, đã có lỗi xảy ra.
            Vui lòng thử lại sau hoặc liên hệ support@decode.com
            """)

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
        finally:
            self.logger.info("Stopping bot...")
            await self.application.stop()