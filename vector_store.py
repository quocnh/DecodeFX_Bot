from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings
from typing import List, Tuple, Optional
import logging
from config import Config

class VectorStore:
    def __init__(self, persist_directory: str = Config.CHROMA_PERSIST_DIR,
                 embedding_model: str = Config.EMBEDDING_MODEL):
        self.logger = logging.getLogger(__name__)
        self.persist_directory = persist_directory
        
        try:
            # Initialize embeddings
            self.embeddings = HuggingFaceEmbeddings(
                model_name=embedding_model,
                model_kwargs={'device': 'cpu'}
            )
            
            # Initialize vector store
            self.vector_store = Chroma(
                persist_directory=persist_directory,
                embedding_function=self.embeddings,
                collection_name=Config.COLLECTION_NAME
            )
            
            self.logger.info("Vector store initialized successfully")
        except Exception as e:
            self.logger.error(f"Error initializing vector store: {str(e)}")
            raise

    def add_documents(self, documents: List) -> None:
        """Add documents to vector store"""
        try:
            self.vector_store.add_documents(documents)
            self.vector_store.persist()
            self.logger.info(f"Added {len(documents)} documents to vector store")
        except Exception as e:
            self.logger.error(f"Error adding documents: {str(e)}")
            raise

    def similarity_search(self, query: str, k: int = 1) -> List[Tuple]:
        """Search for similar documents"""
        try:
            results = self.vector_store.similarity_search_with_score(
                query=query,
                k=k
            )
            return results
        except Exception as e:
            self.logger.error(f"Error in similarity search: {str(e)}")
            return []

    def get_relevant_documents(self, query: str, threshold: float = Config.SIMILARITY_THRESHOLD) -> Optional[str]:
        """Get relevant documents above threshold"""
        try:
            results = self.similarity_search(query)
            if results and results[0][1] <= threshold:
                doc = results[0][0]
                answer = doc.page_content.split("Answer: ")[1].strip()
                return answer
            return None
        except Exception as e:
            self.logger.error(f"Error getting relevant documents: {str(e)}")
            return None