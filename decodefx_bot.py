# Import required libraries
import os
import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

class DecodeCustomerServiceBot:
    def __init__(self, model_name: str = 'vinai/phobert-base'):
        """
        Initialize the customer service bot with necessary components
        """
        self.encoder = SentenceTransformer(model_name)
        self.qa_pairs = []
        self.question_embeddings = None
        self.logger = self._setup_logging()

    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration"""
        logging.basicConfig(
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            level=logging.INFO
        )
        return logging.getLogger(__name__)

    def process_training_data(self, markdown_content: str) -> List[Dict]:
        """
        Process the markdown training data into structured QA pairs
        """
        qa_pairs = []
        current_qa = {}
        
        for line in markdown_content.split('\n'):
            if line.startswith('KHÁCH_HÀNG:'):
                if current_qa:
                    qa_pairs.append(current_qa.copy())
                current_qa = {'question': line.replace('KHÁCH_HÀNG:', '').strip()}
            elif line.startswith('TRẢ_LỜI:'):
                current_qa['answer'] = line.replace('TRẢ_LỜI:', '').strip()
            elif line.startswith('NHÃN:'):
                current_qa['tags'] = eval(line.replace('NHÃN:', '').strip())
            elif line.startswith('ĐỘ_ƯU_TIÊN:'):
                current_qa['priority'] = line.replace('ĐỘ_ƯU_TIÊN:', '').strip()
                
        if current_qa:
            qa_pairs.append(current_qa)
            
        return qa_pairs

    def train(self, qa_pairs: List[Dict]):
        """
        Train the model by creating embeddings for all questions
        """
        self.qa_pairs = qa_pairs
        questions = [pair['question'] for pair in qa_pairs]
        self.question_embeddings = self.encoder.encode(questions)

    def find_best_response(self, query: str, threshold: float = 0.7) -> Tuple[str, float]:
        """
        Find the best response for a given query
        """
        query_embedding = self.encoder.encode([query])
        similarities = cosine_similarity(query_embedding, self.question_embeddings)[0]
        
        best_idx = np.argmax(similarities)
        best_similarity = similarities[best_idx]
        
        if best_similarity < threshold:
            return ("Xin lỗi, tôi không hiểu câu hỏi của bạn. Vui lòng thử lại với cách diễn đạt khác.", 0.0)
        
        return (self.qa_pairs[best_idx]['answer'], best_similarity)

class TelegramInterface:
    def __init__(self, bot: DecodeCustomerServiceBot, token: str):
        """
        Initialize Telegram bot interface
        """
        self.bot = bot
        self.application = Application.builder().token(token).build()
        self.setup_handlers()

    def setup_handlers(self):
        """
        Setup message handlers for Telegram
        """
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

    # async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    #     """
    #     Handle /start command
    #     """
    #     await update.message.reply_text('Xin chào! Tôi là bot hỗ trợ của Decode FX. Tôi có thể giúp gì cho bạn?')

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        welcome_message = """
        Chào mừng bạn đến với Decode FX Support! 👋
        
        Tôi có thể giúp bạn với:
        • Thông tin KYC
        • Nạp/rút tiền
        • Vấn đề giao dịch
        • Hỗ trợ kỹ thuật
        
        Hãy đặt câu hỏi để bắt đầu!
        """
        await update.message.reply_text(welcome_message)


    async def handle_unknown(self, update, context):
        error_message = """
        Xin lỗi, tôi không hiểu câu hỏi của bạn.
        Vui lòng thử:
        • Diễn đạt lại câu hỏi
        • Sử dụng từ ngữ đơn giản hơn
        • Liên hệ support nếu cần thiết
        """
        await update.message.reply_text(error_message)

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handle incoming messages
        """
        query = update.message.text
        response, confidence = self.bot.find_best_response(query)
        await update.message.reply_text(response)

    async def start_bot(self):
        """
        Start the Telegram bot
        """
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling()
        await self.application.updater.idle()

def main():
    # Initialize the customer service bot
    bot = DecodeCustomerServiceBot()
    
    # Load and process training data
    with open('decode-fx-vietnamese-dataset.md', 'r', encoding='utf-8') as f:
        markdown_content = f.read()
    
    qa_pairs = bot.process_training_data(markdown_content)
    bot.train(qa_pairs)
    
    # Initialize and start Telegram interface
    # telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
    telegram_token = "7580620084:AAENgQsXBoMOUvZ38elukY-C1bdYTczCb4c"
    #7580620084:AAENgQsXBoMOUvZ38elukY-C1bdYTczCb4c
    telegram_interface = TelegramInterface(bot, telegram_token)
    
    # Use asyncio to run the bot
    import asyncio
    # asyncio.run(telegram_interface.start_bot())
    asyncio.run(telegram_interface.application.run_polling(drop_pending_updates=True))


if __name__ == "__main__":
    main()