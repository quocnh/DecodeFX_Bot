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
- Try different strategies to get the best response:
    - Try phobert
    - Implements llama_model for for general text generation
    - Try default response

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
Note: rm -rf venv
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
or use Anaconda

### 3. Install requirements
pip install -r requirements.txt

# 4. Run the bot
python main.py
```

flowchart TD
    subgraph External["External Services"]
        TG["Telegram API"]
        HF["HuggingFace Hub"]
    end

    subgraph Main["Main Application"]
        MI["main.py"]
        ENV[".env file"]
        DS["Training Dataset\n(decode-fx-vietnamese-dataset.md)"]
        MI --> |loads| ENV
        MI --> |reads| DS
    end

    subgraph Core["Core Components"]
        TI["TelegramInterface\n(telegram_interface.py)"]
        CSB["DecodeCustomerServiceBot\n(decode_customer_service_bot.py)"]
        LMS["LanguageModelService\n(language_models.py)"]
        
        subgraph Models["AI Models"]
            ST["Sentence Transformer\n(vinai/phobert-base)"]
            L2["Llama-2-7b-chat"]
        end
        
        TI --> |queries| CSB
        CSB --> |uses| LMS
        LMS --> |uses| Models
    end

    MI --> |initializes| TI
    MI --> |initializes| CSB
    TI <--> |interacts| TG
    LMS <--> |downloads| HF

    subgraph Response["Response Strategy"]
        direction TB
        S1["1. Training Data Match\n(Similarity ≥ 0.7)"]
        S2["2. Llama 2 Generation"]
        S3["3. Default Response"]
        
        S1 --> |no match| S2
        S2 --> |failed| S3
    end
