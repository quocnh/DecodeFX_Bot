from langchain.text_splitter import MarkdownTextSplitter
from langchain.docstore.document import Document
import logging
from typing import List, Dict
from config import Config

class DataProcessor:
    def __init__(self, chunk_size: int = Config.CHUNK_SIZE, 
                 chunk_overlap: int = Config.CHUNK_OVERLAP):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.logger = logging.getLogger(__name__)

    def create_documents(self, qa_pairs: List[Dict]) -> List[Document]:
        """Create documents from QA pairs for vector store"""
        docs = []
        for qa in qa_pairs:
            try:
                # Combine question and answer into one document
                text = f"Question: {qa['question']}\nAnswer: {qa['answer']}"
                metadata = {
                    'category': qa.get('category', 'unknown'),
                    'tags': qa.get('tags', []),
                    'priority': qa.get('priority', 'normal'),
                    'type': 'qa_pair'
                }
                docs.append(Document(page_content=text, metadata=metadata))
            except Exception as e:
                self.logger.error(f"Error creating document: {str(e)}")
                continue
        return docs

    def split_documents(self, documents: List[Document]) -> List[Document]:
        """Split documents into chunks"""
        text_splitter = MarkdownTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap
        )
        
        splits = []
        for doc in documents:
            try:
                doc_splits = text_splitter.split_documents([doc])
                splits.extend(doc_splits)
            except Exception as e:
                self.logger.error(f"Error splitting document: {str(e)}")
                continue
                
        return splits

    def preprocess_text(self, text: str) -> str:
        """Preprocess text for better matching"""
        # Normalize text
        text = text.lower().strip()
        
        # Replace common variations
        replacements = {
            'tk': 'tài khoản',
            'đk': 'đăng ký',
            'acc': 'account',
            'mt4': 'metatrader 4',
            'mt5': 'metatrader 5'
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
            
        return text