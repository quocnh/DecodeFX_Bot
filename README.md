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
