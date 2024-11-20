import logging
from typing import Dict, List, Tuple
from language_models import LanguageModelService

class DecodeCustomerServiceBot:
    def __init__(self, huggingface_token: str):
        """
        Initialize the customer service bot with necessary components
        """
        self.logger = self._setup_logging()
        self.language_service = LanguageModelService(huggingface_token)
        self.qa_pairs = []

    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration"""
        logging.basicConfig(
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            level=logging.INFO
        )
        return logging.getLogger(__name__)

    def process_training_data(self, markdown_content: str) -> List[Dict]:
        """
        Process the markdown training data into structured QA pairs
        """
        qa_pairs = []
        current_qa = {}
        
        for line in markdown_content.split('\n'):
            if line.startswith('KHÁCH_HÀNG:'):
                if current_qa:
                    qa_pairs.append(current_qa.copy())
                current_qa = {'question': line.replace('KHÁCH_HÀNG:', '').strip()}
            elif line.startswith('TRẢ_LỜI:'):
                current_qa['answer'] = line.replace('TRẢ_LỜI:', '').strip()
            elif line.startswith('NHÃN:'):
                current_qa['tags'] = eval(line.replace('NHÃN:', '').strip())
            elif line.startswith('ĐỘ_ƯU_TIÊN:'):
                current_qa['priority'] = line.replace('ĐỘ_ƯU_TIÊN:', '').strip()
                
        if current_qa:
            qa_pairs.append(current_qa)
            
        self.logger.info(f"Processed {len(qa_pairs)} QA pairs from training data")
        return qa_pairs

    def train(self, qa_pairs: List[Dict]):
        """Store QA pairs for later use"""
        self.qa_pairs = qa_pairs
        self.logger.info(f"Loaded {len(qa_pairs)} QA pairs for training")

    def find_best_response(self, query: str) -> Tuple[str, float]:
        """
        Find the best response using multiple fallback strategies
        """
        self.logger.info(f"Finding best response for query: {query}")
        return self.language_service.get_best_response(query, self.qa_pairs)