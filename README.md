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
Note:
deactivate
rm -rf venv
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
or use Anaconda

### 3. Install requirements
pip install -r requirements.txt

# 4. Run the bot
python main.py

decode-fx-bot/
├── main.py
├── config.py
├── bot_service.py
├── telegram_interface.py
├── dataset_parser.py
├── logger_config.py
├── requirements.txt
├── .env
├── data/
│   └── dataset.md
└── logs/
    └── .gitkeep
    
```
# Cloud Deployment:

# System Diagram:
```mermaid
graph TD
    subgraph External ["External Systems"]
        TG[Telegram API]
    end

    subgraph Main ["Main Application"]
        M[main.py]
        M -->|initializes| LS[LoggerSetup]
        M -->|creates| BS[BotService]
        M -->|creates| TI[TelegramInterface]
    end

    subgraph Core ["Core Services"]
        BS -->|uses| DP[DatasetParser]
        BS -->|uses| ST[Sentence Transformer]
        BS -->|reads| CF[Config]
        TI -->|uses| BS
        TI -->|reads| CF
    end

    subgraph Data ["Data Layer"]
        DP -->|reads| DS[dataset.md]
        CF -->|loads| ENV[.env]
    end

    subgraph Logging ["Logging System"]
        LS -->|writes| LOG[bot.log]
        BS -->|logs| LOG
        TI -->|logs| LOG
    end

    TI <-->|interacts| TG

    subgraph Flow ["Message Flow"]
        direction LR
        U[User] -->|sends message| TG
        TG -->|webhook| TI
        TI -->|processes| BS
        BS -->|generates| R[Response]
        R -->|via| TI
        TI -->|sends| U
    end

classDef external fill:#f9f,stroke:#333,stroke-width:4px
classDef main fill:#bbf,stroke:#333,stroke-width:2px
classDef core fill:#bfb,stroke:#333,stroke-width:2px
classDef data fill:#fbb,stroke:#333,stroke-width:2px
classDef logging fill:#fff,stroke:#333,stroke-width:2px
classDef flow fill:#ffe,stroke:#333,stroke-width:2px

class TG external
class M,TI main
class BS,DP,ST,CF core
class DS,ENV data
class LS,LOG logging
class U,R flow
```
# Sequence Diagram:
```mermaid
sequenceDiagram
    participant U as User
    participant TI as TelegramInterface
    participant BS as BotService
    participant DP as DatasetParser
    participant ST as SentenceTransformer
    participant L as Logger

    U->>+TI: Send Message
    TI->>L: Log incoming message
    
    alt Private Chat
        TI->>BS: Process direct message
    else Group Chat
        TI->>TI: Check bot mention/reply
        TI->>BS: Process if bot mentioned
    end
    
    BS->>ST: Generate embeddings
    BS->>BS: Check general patterns
    
    alt Pattern Match Found
        BS-->>TI: Return general response
    else No Pattern Match
        BS->>ST: Compare with dataset
        ST-->>BS: Return similarities
        BS->>BS: Check confidence threshold
        alt High Confidence
            BS-->>TI: Return dataset response
        else Low Confidence
            BS-->>TI: Return default response
        end
    end
    
    TI->>L: Log response
    TI-->>-U: Send Response
```
