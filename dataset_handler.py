from typing import List, Dict
import logging
import os
from config import Config

class DatasetHandler:
    def __init__(self, dataset_path: str = Config.DATASET_PATH):
        self.dataset_path = dataset_path
        self.logger = logging.getLogger(__name__)
        self.categories = {
            'account_management': '1. QUẢN LÝ TÀI KHOẢN',
            'trading': '2. GIAO DỊCH',
            'deposits_withdrawals': '3. NẠP/RÚT TIỀN',
            'promotions': '4. CHƯƠNG TRÌNH KHUYẾN MÃI',
            'copy_trading': '5. COPY TRADE',
            'compliance': '6. COMPLIANCE VÀ KYC',
            'technical_issues': '7. VẤN ĐỀ KỸ THUẬT',
            'liquidity': '8. VẤN ĐỀ THANH KHOẢN VÀ SPREAD'
        }

    def load_dataset(self) -> str:
        """Load the markdown dataset"""
        try:
            if not os.path.exists(self.dataset_path):
                raise FileNotFoundError(f"Dataset file not found: {self.dataset_path}")
                
            with open(self.dataset_path, 'r', encoding='utf-8') as f:
                content = f.read()
            self.logger.info(f"Successfully loaded dataset from {self.dataset_path}")
            return content
        except Exception as e:
            self.logger.error(f"Error loading dataset: {str(e)}")
            raise

    def extract_qa_pairs(self, content: str) -> List[Dict]:
        """Extract QA pairs from content"""
        qa_pairs = []
        current_qa = {}
        current_category = None
        
        for line in content.split('\n'):
            line = line.strip()
            if not line:
                continue
                
            if line.startswith('##'):
                current_category = line.strip('# ')
            elif line.startswith('KHÁCH_HÀNG:'):
                if current_qa:
                    qa_pairs.append(current_qa.copy())
                current_qa = {
                    'question': line.replace('KHÁCH_HÀNG:', '').strip(),
                    'category': current_category
                }
            elif line.startswith('TRẢ_LỜI:'):
                current_qa['answer'] = line.replace('TRẢ_LỜI:', '').strip()
            elif line.startswith('NHÃN:'):
                current_qa['tags'] = eval(line.replace('NHÃN:', '').strip())
            elif line.startswith('ĐỘ_ƯU_TIÊN:'):
                current_qa['priority'] = line.replace('ĐỘ_ƯU_TIÊN:', '').strip()
                
        if current_qa:
            qa_pairs.append(current_qa)
            
        return qa_pairs

    def get_statistics(self) -> Dict:
        """Get dataset statistics"""
        content = self.load_dataset()
        qa_pairs = self.extract_qa_pairs(content)
        
        stats = {
            'total_qa_pairs': len(qa_pairs),
            'categories': {},
            'priorities': {
                'khẩn_cấp': 0,
                'cao': 0,
                'trung_bình': 0,
                'thấp': 0
            },
            'tags': {}
        }
        
        for qa in qa_pairs:
            # Count by category
            category = qa.get('category', 'unknown')
            stats['categories'][category] = stats['categories'].get(category, 0) + 1
            
            # Count by priority
            priority = qa.get('priority', 'unknown')
            stats['priorities'][priority] = stats['priorities'].get(priority, 0) + 1
            
            # Count tags
            for tag in qa.get('tags', []):
                stats['tags'][tag] = stats['tags'].get(tag, 0) + 1
                
        return stats

    def validate_dataset(self) -> List[str]:
        """Validate dataset structure and content"""
        errors = []
        content = self.load_dataset()
        qa_pairs = self.extract_qa_pairs(content)
        
        for i, qa in enumerate(qa_pairs):
            # Check required fields
            if 'question' not in qa:
                errors.append(f"QA pair {i+1} missing question")
            if 'answer' not in qa:
                errors.append(f"QA pair {i+1} missing answer")
                
            # Check field content
            if qa.get('question', '').strip() == '':
                errors.append(f"QA pair {i+1} has empty question")
            if qa.get('answer', '').strip() == '':
                errors.append(f"QA pair {i+1} has empty answer")
                
            # Validate priority values
            if qa.get('priority') not in ['khẩn_cấp', 'cao', 'trung_bình', 'thấp']:
                errors.append(f"QA pair {i+1} has invalid priority: {qa.get('priority')}")
                
        return errors