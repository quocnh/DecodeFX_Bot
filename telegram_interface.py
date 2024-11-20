from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
import logging

class TelegramInterface:
    def __init__(self, bot, token: str):
        """
        Initialize Telegram bot interface
        """
        self.logger = logging.getLogger(__name__)
        self.bot = bot
        self.application = Application.builder().token(token).build()
        self.setup_handlers()

    def setup_handlers(self):
        """
        Setup message handlers for Telegram
        """
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("help", self.help))
        self.application.add_handler(MessageHandler(
            (filters.TEXT & ~filters.COMMAND & (filters.ChatType.GROUPS | filters.ChatType.PRIVATE)),
            self.handle_message
        ))
        self.logger.info("Telegram handlers set up successfully")

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handle /start command
        """
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
        self.logger.info(f"Start command received from user {update.effective_user.id}")

    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handle /help command
        """
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
        self.logger.info(f"Help command received from user {update.effective_user.id}")

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handle incoming messages from both private chats and groups
        """
        chat_type = update.message.chat.type
        chat_id = update.message.chat_id
        user_id = update.effective_user.id
        query = update.message.text

        self.logger.info(f"Received message from user {user_id} in {chat_type} chat {chat_id}: {query}")

        try:
            # Handle group messages differently
            if chat_type in ['group', 'supergroup']:
                if not (query.startswith('/') or f'@{context.bot.username}' in query):
                    return
                
            response, confidence = self.bot.find_best_response(query)
            
            self.logger.info(f"Generated response with confidence {confidence}")
            await update.message.reply_text(response)
            
        except Exception as e:
            self.logger.error(f"Error handling message: {e}")
            error_message = """
            Xin lỗi, đã có lỗi xảy ra.
            Vui lòng thử lại sau hoặc liên hệ support@decode.com
            """
            await update.message.reply_text(error_message)