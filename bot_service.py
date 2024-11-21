from typing import Tuple, Optional
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import logging
import re
from dataset_parser import DatasetParser
from config import Config

class BotService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.confidence_threshold = Config.CONFIDENCE_THRESHOLD
        self.model = SentenceTransformer('VoVanPhuc/sup-SimCSE-VietNamese-phobert-base')
        
        # Load dataset using the parser
        self.dataset_parser = DatasetParser()
        self.qa_pairs = self.dataset_parser.parse_markdown_file(Config.DATASET_PATH)
        self.questions = [pair['KHÁCH_HÀNG'] for pair in self.qa_pairs]
        self.question_embeddings = self._compute_embeddings(self.questions)
        
        # Define general patterns
        self.general_patterns = Config.GENERAL_PATTERNS
        self.default_response = Config.DEFAULT_RESPONSE

    def _compute_embeddings(self, texts: list) -> np.ndarray:
        """Compute embeddings for a list of texts"""
        try:
            return self.model.encode(texts, convert_to_tensor=True)
        except Exception as e:
            self.logger.error(f"Error computing embeddings: {str(e)}")
            return np.array([])

    def _check_general_patterns(self, query: str) -> Optional[str]:
        """Check if query matches any general patterns"""
        query = query.lower().strip()
        
        for pattern_group in self.general_patterns:
            for pattern in pattern_group['patterns']:
                if re.search(pattern, query):
                    return pattern_group['response']
        return None

    def get_response(self, query: str, user_id: str, username: str) -> Tuple[str, float]:
        """Get response for user query"""
        try:
            # Log incoming query
            self.logger.info(f"Processing query from {username} ({user_id}): {query}")
            
            # First check general patterns
            general_response = self._check_general_patterns(query)
            if general_response:
                self.logger.info(f"Found general pattern match for query: {query}")
                return general_response, 1.0
            
            # If no general pattern matches, try specific QA matching
            query_embedding = self.model.encode([query], convert_to_tensor=True)
            similarities = cosine_similarity(
                query_embedding.numpy(),
                self.question_embeddings.numpy()
            )[0]
            
            best_match_idx = np.argmax(similarities)
            confidence = similarities[best_match_idx]
            
            if confidence >= self.confidence_threshold:
                response = self.qa_pairs[best_match_idx]['TRẢ_LỜI']
                priority = self.qa_pairs[best_match_idx]['ĐỘ_ƯU_TIÊN']
                
                self.logger.info(
                    f"Found match: Confidence={confidence:.2f}, Priority={priority}"
                )
                
                # Add contact info for moderate confidence
                if confidence < 0.85:
                    response += Config.MODERATE_CONFIDENCE_SUFFIX
                    
                return response, confidence
            
            self.logger.info(
                f"No good match found. Best confidence: {confidence:.2f}"
            )
            return self.default_response, confidence

        except Exception as e:
            self.logger.error(f"Error getting response: {str(e)}")
            return self.default_response, 0.0

    def prepare_response(self, response: str) -> str:
        """Clean and format the response"""
        try:
            response = response.strip()
            response = response.replace('  ', ' ')
            
            # Add emoji based on content
            if "xin lỗi" in response.lower():
                response = "😅 " + response
            elif "cảm ơn" in response.lower():
                response = "😊 " + response
            
            return response
        except Exception as e:
            self.logger.error(f"Error preparing response: {str(e)}")
            return self.default_response
