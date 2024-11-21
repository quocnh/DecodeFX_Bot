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
python -m venv venv
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

```mermaid
flowchart TD
    subgraph User["User Interface"]
        TG["Telegram\nClient"]
    end

    subgraph Dataset["Training Dataset"]
        MD["Markdown Dataset\ndecode-fx-vietnamese-dataset.md"]
        subgraph DataStructure["Data Structure"]
            QS["KHÁCH_HÀNG:\nQuestions"]
            AN["TRẢ_LỜI:\nAnswers"]
            TG1["NHÃN:\nTags"]
            PR["ĐỘ_ƯU_TIÊN:\nPriority"]
        end
        MD --> |contains| DataStructure
    end

    subgraph Core["Core Components"]
        TI["TelegramInterface\n(telegram_interface.py)"]
        BS["BotService\n(bot_service.py)"]
        
        subgraph DataProcessing["Data Processing"]
            DP["DataProcessor\n(data_processor.py)"]
            QA["QA Pairs"]
            DC["Document Chunks"]
            DP --> |extract| QA
            QA --> |split| DC
        end
        
        subgraph VectorDB["Vector Store"]
            VS["VectorStore\n(vector_store.py)"]
            CH["ChromaDB"]
            EM["Embeddings\n(PhoBERT)"]
            VS --> |store| CH
            VS --> |embed| EM
        end
        
        subgraph LLM["Language Model"]
            LS["LLMService\n(llm_service.py)"]
            L2["Llama Model"]
            TK["Tokenizer"]
            LS --> |use| L2
            LS --> |use| TK
        end
        
        subgraph Config["Configuration"]
            CF["config.py"]
            ENV[".env file"]
            CF --> |load| ENV
        end
    end

    %% Dataset to Processing Flow
    MD --> |input| DP
    DataStructure --> |structure| QA

    %% Data Flow
    TG <--> |messages| TI
    TI --> |query| BS
    BS --> |search| VS
    BS --> |generate| LS
    DC --> |index| VS

    %% Return Flow
    VS --> |results| BS
    LS --> |response| BS
    BS --> |response| TI
    
    %% Styles
    style User fill:#e6f3ff,stroke:#333
    style Core fill:#f5f5f5,stroke:#333
    style Dataset fill:#ffe6cc,stroke:#333
    style DataProcessing fill:#fff2e6,stroke:#333
    style VectorDB fill:#e6ffe6,stroke:#333
    style LLM fill:#ffe6e6,stroke:#333
    style Config fill:#e6e6ff,stroke:#333
    style DataStructure fill:#fff5e6,stroke:#333

    %% Component Relationships
    CF -.-> |configure| TI
    CF -.-> |configure| VS
    CF -.-> |configure| LS

    %% Dataset Organization Notes
    subgraph DatasetNotes["Dataset Organization"]
        direction TB
        N1["1. Account Management"]
        N2["2. Trading"]
        N3["3. Deposits/Withdrawals"]
        N4["4. Promotions"]
        N5["5. Copy Trading"]
        N6["...Other Categories"]
    end
    
    MD -.-> |organized into| DatasetNotes
```
