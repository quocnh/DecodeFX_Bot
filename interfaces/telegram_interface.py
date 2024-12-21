from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from config import TELEGRAM_TOKEN, DEFAULT_RESPONSE, logger
from datetime import datetime

class TelegramInterface:
    def __init__(self, bot_model):
        logger.info("Initializing Enhanced Telegram Interface")
        self.bot_model = bot_model
        self.app = Application.builder().token(TELEGRAM_TOKEN).build()
        
        # Add handlers
        self.app.add_handler(CommandHandler("start", self.start_command))
        self.app.add_handler(MessageHandler(
            (filters.TEXT & ~filters.COMMAND) & 
            (filters.ChatType.PRIVATE | filters.ChatType.GROUPS), 
            self.handle_message
        ))
        
        # Store conversation context
        self.conversation_context = {}

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        username = update.effective_user.username
        chat_type = update.effective_chat.type
        
        logger.info(f"Start command received from User ID: {user_id}, Username: {username}, Chat Type: {chat_type}")
        
        await update.message.reply_text(
            "Xin chào! Tôi là bot hỗ trợ của DecodeFX. Tôi có thể giúp gì cho bạn?"
        )

    def should_respond(self, update: Update) -> bool:
        chat_type = update.effective_chat.type
        message = update.message
        bot_username = self.app.bot.username

        # Always respond in private chats
        if chat_type == 'private':
            logger.info("Responding to private chat message")
            return True

        # In groups, check for mentions
        if chat_type in ['group', 'supergroup']:
            if message.entities:
                for entity in message.entities:
                    if entity.type == 'mention':
                        mentioned = message.text[entity.offset:entity.offset + entity.length]
                        if mentioned == f"@{bot_username}":
                            logger.info("Responding to group message with direct mention")
                            return True
            return False

        return False

    def extract_question(self, message_text: str, bot_username: str) -> str:
        # Remove bot username from the message
        clean_text = message_text.replace(f"@{bot_username}", "").strip()
        return clean_text

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            # Check if we should respond
            if not self.should_respond(update):
                return

            # Log incoming message details
            user_id = update.effective_user.id
            username = update.effective_user.username
            chat_type = update.effective_chat.type
            message_text = update.message.text
            chat_id = update.effective_chat.id
            
            logger.info(f"""
                Received message:
                User ID: {user_id}
                Username: {username}
                Chat Type: {chat_type}
                Message: {message_text}
            """.strip())
            
            # Extract the actual question
            question = self.extract_question(message_text, self.app.bot.username)
            
            # Get chat context if available
            chat_context = self.conversation_context.get(chat_id, {})
            
            # Process message
            try:
                answer = self.bot_model.find_best_answer(
                    question,
                    chat_id=str(chat_id),
                    context=chat_context.get('last_message'),
                    previous_response=chat_context.get('last_response')
                )
            except Exception as e:
                logger.error(f"Error getting answer from bot model: {str(e)}")
                answer = None
            
            if answer:
                logger.info(f"Sending answer to User {user_id}: {answer[:100]}...")
                await update.message.reply_text(answer)
                # Update conversation context
                self.conversation_context[chat_id] = {
                    'last_message': message_text,
                    'last_response': answer,
                    'timestamp': datetime.now().timestamp()
                }
            else:
                logger.info(f"Sending default response to User {user_id}")
                await update.message.reply_text(DEFAULT_RESPONSE)
                
        except Exception as e:
            logger.error(f"Error handling message: {str(e)}")
            await update.message.reply_text(
                "Xin lỗi, có lỗi xảy ra. Vui lòng thử lại sau hoặc liên hệ bộ phận CSKH."
            )

    def run(self):
        logger.info("Starting Enhanced Telegram bot")
        self.app.run_polling()