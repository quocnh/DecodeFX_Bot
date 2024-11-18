# DecodeFX_Bot
A complete pipeline for DEcodeFX customer service chatbot.

## 1. Data Processing:

- Processes the markdown dataset into structured QA pairs
- Extracts questions, answers, tags, and priorities
- Maintains context information for better response matching


## 2. Core Bot Engine:

- Uses SentenceTransformer with phobert-base (optimized for Vietnamese)
- Creates embeddings for all questions in the dataset
- Uses cosine similarity to find the best matching response
- Implements confidence threshold for fallback responses


## 3. Telegram Integration:

- Handles incoming messages and commands
- Provides a simple interface for users
- Manages bot lifecycle and error handling

# Local Deployment (For Testing):
```python
### 1. Create a directory for your bot
mkdir decodefx-bot
cd decodefx-bot

### 2. Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

### 3. Install requirements
pip install telebot python-telegram-bot sentence-transformers scikit-learn pandas numpy

### 4. Add your bot token
export TELEGRAM_BOT_TOKEN="your_token_here"

# 5. Run the bot
python customer_service_bot.py
```
