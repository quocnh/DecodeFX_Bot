# DecodeFX_Bot

The DecodeFX Support Bot is an advanced customer service chatbot designed specifically for the forex trading platform DecodeFX. Built using state-of-the-art natural language processing techniques, the bot provides instant, accurate responses to customer inquiries in both Vietnamese and English, focusing on trading-related questions, account management, and platform support.
## Key Features
### Multilingual Support

- Seamlessly handles both Vietnamese and English queries
- Processes Vietnamese text with or without diacritics
- Understands informal language and regional variations

### Intelligent Query Processing

- Uses semantic similarity matching for accurate response selection
- Handles misspellings and partial words
- Implements fuzzy matching for better query understanding
- Provides confirmation requests for ambiguous queries

### Context-Aware Conversations

- Maintains conversation context for better response accuracy
- Understands follow-up questions
- Processes conversation history for more relevant responses

### Advanced Natural Language Processing

- Employs the SentenceTransformer model for semantic understanding
- Uses smart confirmation detection for natural dialogue flow
- Implements context mapping for better response accuracy

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
# Deactivate current environment
deactivate

# Remove the old virtual environment
rm -rf venv

# Create new virtual environment
python3.11 -m venv venv

# Activate the new environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt

DecodeFX_Bot/
├── .env                    # Environment variables
├── requirements.txt        # Dependencies
├── data/                   # Data directory
│   └── decode-fx-vietnamese-dataset.md
├── logs/                   # Log files directory
├── models/                 # Models directory
│   ├── __init__.py        # Make models a package
│   └── bot_llm.py
├── interfaces/            # Interfaces directory
│   ├── __init__.py       # Make interfaces a package
│   └── telegram_interface.py
├── config.py             # Configuration file
└── main.py              # Main application file
    
```
# Cloud Deployment:

# System Diagram:
```mermaid
graph TB
    User[User/Customer] --> TG[Telegram Client]
    
    subgraph "DecodeFX Bot System"
        TG --> TI[Telegram Interface]
        TI --> Logger[Logging System]
        TI --> BLLM[BotLLMModel]
        
        subgraph "BotLLMModel Components"
            BLLM --> ST[Sentence Transformer]
            BLLM --> DS[Dataset Handler]
            ST --> SM[Similarity Matcher]
        end
        
        DS --> MD[(Vietnamese Q&A Dataset)]
        Logger --> LF[(Log Files)]
    end
    
    classDef primary fill:#f9f,stroke:#333,stroke-width:2px
    classDef secondary fill:#bbf,stroke:#333,stroke-width:2px
    classDef storage fill:#dfd,stroke:#333,stroke-width:2px
    
    class TI,BLLM primary
    class ST,DS,SM,Logger secondary
    class MD,LF storage
```
# Sequence Diagram:
```mermaid
sequenceDiagram
    participant U as User
    participant T as Telegram
    participant TI as TelegramInterface
    participant L as Logger
    participant B as BotLLMModel
    participant ST as SentenceTransformer
    participant D as Dataset

    %% Initialization
    Note over TI,D: System Initialization
    TI->>B: Initialize
    B->>ST: Load Model
    B->>D: Load Dataset
    B->>ST: Generate Embeddings

    %% Message Flow
    U->>T: Send Message
    T->>TI: Forward Message
    TI->>L: Log Incoming Message
    
    alt Private Chat
        TI->>TI: Process Directly
    else Group Chat
        TI->>TI: Check if Bot Mentioned
    end

    alt General/Short Query
        TI->>B: find_best_answer(query)
        B->>B: _is_general_query(query)
        B->>B: _get_sample_questions()
        B-->>TI: Return Sample Questions
    else Specific Query
        TI->>B: find_best_answer(query)
        B->>ST: Generate Query Embedding
        B->>B: Calculate Similarity
        alt Good Match Found
            B-->>TI: Return Best Answer
        else No Good Match
            B-->>TI: Return Default Response
        end
    end
    
    TI->>L: Log Response
    TI->>T: Send Response
    T->>U: Display Response
```
