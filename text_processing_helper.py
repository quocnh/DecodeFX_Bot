from difflib import SequenceMatcher
import re
from typing import List, Tuple, Dict

class TextProcessor:
    def __init__(self):
        # Common Vietnamese word starts
        self.word_starts = {
            'b': ['bên', 'bạn', 'bao', 'bonus', 'btc'],
            'k': ['khách', 'không', 'khi', 'kyc'],
            't': ['tiền', 'tài', 'trade', 'trading'],
            'đ': ['đầu', 'được', 'đăng', 'đóng'],
            'n': ['nạp', 'nhận', 'người', 'ngân'],
            'm': ['mình', 'margin', 'mt4', 'mua'],
            'r': ['rút', 'rebate', 'rồi', 'review'],
            's': ['sàn', 'swap', 'server', 'số'],
            'c': ['commission', 'com', 'copy', 'cần'],
            'g': ['giao', 'giá', 'gì', 'group']
        }
        
        # Common Vietnamese words in trading context
        self.common_words = {
            'ben': 'bên',
            'khach': 'khách',
            'tien': 'tiền',
            'minh': 'mình',
            'san': 'sàn',
            'nap': 'nạp',
            'dau': 'đầu',
            'duoc': 'được',
            'khong': 'không',
            'gi': 'gì',
            'the': 'thế',
            'nao': 'nào'
        }
        
        # Common question patterns
        self.question_patterns = [
            r'(.*?) có (.*?) không',
            r'(.*?) sao (.*?)',
            r'(.*?) như thế nào',
            r'làm sao (.*?)',
            r'(.*?) là gì',
            r'bao (.*?)',
            r'khi nào (.*?)'
        ]

    def fix_partial_word(self, word: str) -> str:
        """Fix partial words based on first letter and context"""
        if len(word) <= 1:
            return word
            
        first_char = word[0].lower()
        if first_char in self.word_starts:
            possible_words = self.word_starts[first_char]
            best_match = None
            best_ratio = 0
            
            for possible in possible_words:
                ratio = SequenceMatcher(None, word, possible).ratio()
                if ratio > best_ratio and ratio > 0.5:  # Threshold for matching
                    best_ratio = ratio
                    best_match = possible
                    
            return best_match if best_match else word
        return word

    def normalize_text(self, text: str) -> str:
        """Normalize Vietnamese text with diacritics"""
        # Basic mapping for common cases
        for wrong, correct in self.common_words.items():
            text = re.sub(r'\b' + wrong + r'\b', correct, text, flags=re.IGNORECASE)
            
        return text

    def find_similar_question(self, partial_question: str, question_bank: List[str]) -> Tuple[str, float]:
        """Find the most similar question from the question bank"""
        best_match = None
        best_ratio = 0
        
        normalized_partial = self.normalize_text(partial_question.lower())
        
        for question in question_bank:
            normalized_q = self.normalize_text(question.lower())
            ratio = SequenceMatcher(None, normalized_partial, normalized_q).ratio()
            
            if ratio > best_ratio:
                best_ratio = ratio
                best_match = question
                
        return best_match, best_ratio

    def fix_question(self, text: str) -> Tuple[str, bool, str]:
        """
        Fix the question text and determine if confirmation is needed
        Returns: (fixed_text, needs_confirmation, original_question)
        """
        words = text.split()
        fixed_words = []
        needs_fix = False
        
        for word in words:
            fixed_word = self.fix_partial_word(word)
            if fixed_word != word:
                needs_fix = True
            fixed_words.append(fixed_word)
            
        fixed_text = ' '.join(fixed_words)
        fixed_text = self.normalize_text(fixed_text)
        
        # If significant changes were made, suggest confirmation
        if needs_fix:
            return fixed_text, True, text
            
        return fixed_text, False, text

    def is_similar_question(self, q1: str, q2: str, threshold: float = 0.8) -> bool:
        """Check if two questions are similar"""
        return SequenceMatcher(None, q1.lower(), q2.lower()).ratio() > threshold