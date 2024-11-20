from vector_store import VectorStore
from llm_service import LLMService
from config import Config
import logging
from typing import Tuple, Optional

class BotService:
    def __init__(self, vector_store: VectorStore, llm_service: LLMService):
        self.vector_store = vector_store
        self.llm_service = llm_service
        self.logger = logging.getLogger(__name__)
        self.default_response = """
        Xin lỗi, tôi không thể trả lời câu hỏi này.
        Vui lòng:
        • Diễn đạt lại câu hỏi một cách rõ ràng hơn
        • Liên hệ với bộ phận hỗ trợ khách hàng qua email support@decode.com
        • Hoặc gọi hotline: 1900-xxx-xxx
        """

    def get_response(self, query: str) -> Tuple[str, float]:
        """Get response using vector store or LLM"""
        try:
            # First try vector store
            self.logger.info(f"Attempting to find response for query: {query}")
            vector_response = self.vector_store.get_relevant_documents(
                query, 
                threshold=Config.SIMILARITY_THRESHOLD
            )
            
            if vector_response:
                self.logger.info("Found response in vector store")
                return vector_response, 0.9
            
            # If no match in vector store, try LLM
            self.logger.info("No match in vector store, trying LLM")
            llm_response = self.llm_service.generate_response(query)
            
            if llm_response:
                self.logger.info("Generated response using LLM")
                return llm_response, 0.5
            
            # If both fail, return default response
            self.logger.warning("No response generated, using default")
            return self.default_response, 0.0
            
        except Exception as e:
            self.logger.error(f"Error getting response: {str(e)}")
            return self.default_response, 0.0

    def prepare_response(self, response: str) -> str:
        """Format and clean response"""
        try:
            response = response.strip()
            # Add formatting if needed
            if not any(response.startswith(prefix) for prefix in ["Dạ ", "Vâng ", "Xin "]):
                response = "Dạ " + response[0].lower() + response[1:]
            return response
        except Exception as e:
            self.logger.error(f"Error preparing response: {str(e)}")
            return response