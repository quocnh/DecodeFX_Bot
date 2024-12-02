from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import random
import re
from config import logger

class BotLLMModel:
    def __init__(self, dataset_path):
        logger.info("Initializing BotLLMModel")
        try:
            self.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
            # Load original questions and answers
            self.original_questions, self.answers = self._load_md_dataset(dataset_path)
            # Create normalized questions for embedding
            self.normalized_questions = [self._refine_query(q) for q in self.original_questions]
            # Generate embeddings using normalized questions
            self.question_embeddings = self.model.encode(self.normalized_questions)
            logger.info(f"Successfully loaded dataset with {len(self.original_questions)} QA pairs")
        except Exception as e:
            logger.error(f"Error initializing BotLLMModel: {str(e)}")
            raise

    def _extract_qa_from_block(self, block):
        """Extract question and answer from a QA block"""
        try:
            lines = block.strip().split('\n')
            question = None
            answer_lines = []
            collecting_answer = False
            
            for line in lines:
                line = line.strip()
                
                if line.startswith('KHÁCH_HÀNG:'):
                    # Extract question text between quotes
                    start = line.find('"')
                    end = line.rfind('"')
                    if start != -1 and end != -1:
                        question = line[start + 1:end]
                
                elif line.startswith('TRẢ_LỜI:'):
                    # Start collecting answer lines
                    collecting_answer = True
                    # Get first line of answer if it's on the same line
                    start = line.find('"')
                    if start != -1:
                        first_answer_line = line[start + 1:]
                        if first_answer_line:
                            answer_lines.append(first_answer_line)
                
                elif collecting_answer and not line.startswith('NHÃN:'):
                    # Continue collecting answer lines until we hit NHÃN
                    # Remove quotes if present
                    line = line.strip('"')
                    if line:
                        answer_lines.append(line)
                
                elif line.startswith('NHÃN:'):
                    collecting_answer = False
            
            # Join answer lines with proper line breaks
            answer = '\n'.join(answer_lines) if answer_lines else None
            
            # Clean up any remaining quotes
            if answer:
                answer = answer.strip('"')
            
            logger.debug(f"Extracted Q: {question}")
            logger.debug(f"Extracted A: {answer}")
            
            return question, answer
            
        except Exception as e:
            logger.error(f"Error parsing QA block: {str(e)}")
            return None, None

    def _load_md_dataset(self, file_path):
        """Load Q&A pairs from markdown file."""
        questions = []
        answers = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                
            # Split content into QA blocks (separated by double newlines)
            qa_blocks = [block for block in content.split('\n\n') if block.strip()]
            
            for block in qa_blocks:
                question, answer = self._extract_qa_from_block(block)
                if question and answer:
                    # Store original questions and answers
                    questions.append(question)
                    answers.append(answer)
                    logger.debug(f"Loaded QA pair - Q: {question[:50]}...")
                    
            logger.info(f"Successfully parsed {len(questions)} QA pairs from markdown file")
            return questions, answers
            
        except Exception as e:
            logger.error(f"Error loading markdown dataset: {str(e)}")
            raise

    def _is_general_query(self, query):
        """Check if the query is too general or too short"""
        greetings = ['hello', 'hi', 'xin chào', 'chào', 'alo', 'hey']
        return (len(query.split()) <= 2 or 
                query.lower() in greetings or 
                len(query) < 5)

    def _get_sample_questions(self, n=5):
        """Return n random sample questions from the dataset"""
        suitable_questions = [q for q in self.original_questions if 10 <= len(q) <= 100]
        if len(suitable_questions) > n:
            samples = random.sample(suitable_questions, n)
        else:
            samples = suitable_questions
        return samples

    def _is_keyword_query(self, query: str) -> bool:
        """Check if the query is just a keyword or very short phrase"""
        keywords = {
            'KYC': 'xác minh danh tính',
            'MT4': 'platform giao dịch',
            'USDT': 'tiền điện tử',
            'BTC': 'bitcoin',
            'ECN': 'tài khoản ECN',
            'IB': 'đối tác giới thiệu',
            'PAMM': 'quản lý vốn',
            'SWAP': 'phí qua đêm',
            'BONUS': 'khuyến mãi',
            'COMMISSION': 'hoa hồng',
            'FREESWAP': 'miễn phí qua đêm',
            'MARGIN': 'ký quỹ',
            'LOT': 'khối lượng giao dịch'
        }
        
        # Clean and normalize query
        clean_query = self._refine_query(query)
        
        # Check if query is just a keyword
        for keyword in keywords:
            if clean_query.upper() == keyword:
                return True, keyword
                
        return False, None

    def _find_related_questions(self, keyword: str, max_questions: int = 5) -> list:
        """Find questions related to a specific keyword"""
        related_questions = []
        
        # Create keyword embedding
        keyword_embedding = self.model.encode([keyword])[0]
        
        # Get similarities with all questions
        similarities = cosine_similarity([keyword_embedding], self.question_embeddings)[0]
        
        # Get indices of top matching questions
        top_indices = np.argsort(similarities)[-max_questions:][::-1]
        
        # Get the questions and their similarities
        for idx in top_indices:
            if similarities[idx] > 0.3:  # Minimum similarity threshold
                related_questions.append({
                    'question': self.original_questions[idx],
                    'similarity': similarities[idx]
                })
        
        return related_questions

    def _refine_query(self, query: str) -> str:
        """Refine and normalize the query for better matching."""
        # Step 1: Normalize whitespace
        query = re.sub(r"\s+", " ", query.strip())
        
        # Step 2: Remove unnecessary punctuation (except for essential ones)
        query = re.sub(r"[^\w\s.,?!]", "", query)
        
        # Step 3: Convert to lowercase for consistency
        query = query.lower()
        
        # Step 4: Replace common variations of keywords with standard forms
        keyword_mapping = {
            'kyc': 'KYC',
            'mt4': 'MT4',
            'usdt': 'USDT',
            'btc': 'BTC',
            'ecn': 'ECN',
            'ib': 'IB',
            'pamm': 'PAMM',
            'swap': 'SWAP',
            'bonus': 'BONUS',
            'commission': 'COMMISSION',
            'freeswap': 'FREESWAP',
            'margin': 'MARGIN',
            'lot': 'LOT'
        }
        
        for key, value in keyword_mapping.items():
            # Use word boundaries to avoid partial replacements
            query = re.sub(rf'\b{key}\b', value, query, flags=re.IGNORECASE)
        
        # Step 5: Handle common verbose phrases
        transformations = {
            "can you please": "please",
            "i would like to know": "tell me",
            "could you": "please",
            "i am wondering": "tell me",
            "cho mình hỏi": "hỏi",
            "cho em hỏi": "hỏi",
            "chị ơi": "",
            "anh ơi": "",
            "em ơi": ""
        }
        for phrase, replacement in transformations.items():
            query = query.replace(phrase, replacement)
        
        # Step 6: Remove stopwords
        stopwords = {"the", "a", "an", "is", "am", "are", "was", "were", "and", "or", "về", "của", "này"}
        tokens = query.split()
        tokens = [token for token in tokens if token.lower() not in stopwords]
        
        # Reassemble refined query
        refined_query = " ".join(tokens)
        
        logger.debug(f"Refined query: {refined_query}")
        return refined_query

    def find_best_answer(self, raw_query, threshold=0.6):
        """Find the best matching answer for a given query."""
        try:
            query = self._refine_query(raw_query)
            logger.info(f"Processing query: {query}")

            # Check if query is too general
            if self._is_general_query(query):
                sample_questions = self._get_sample_questions()
                response = "Xin chào! Bạn có thể hỏi tôi những câu hỏi như:\n\n"
                for i, question in enumerate(sample_questions, 1):
                    response += f"{i}. {question}\n"
                logger.info("Returning sample questions for general query")
                return response

            # Check if query is a keyword
            is_keyword, keyword = self._is_keyword_query(query)
            if is_keyword:
                related = self._find_related_questions(keyword)
                if related:
                    response = f"Có một số câu hỏi liên quan đến {keyword}:\n\n"
                    for i, q in enumerate(related, 1):
                        response += f"{i}. {q['question']}\n"
                    response += "\nBạn có thể hỏi cụ thể hơn về vấn đề bạn quan tâm?"
                    logger.info(f"Returning related questions for keyword: {keyword}")
                    return response

            # Normal processing for specific queries
            query_embedding = self.model.encode([query])
            similarities = cosine_similarity(query_embedding, self.question_embeddings)[0]
            best_match_idx = np.argmax(similarities)
            best_similarity = similarities[best_match_idx]
            
            logger.debug(f"Best match similarity: {best_similarity}")
            logger.debug(f"Best matching question: {self.original_questions[best_match_idx]}")
            
            if best_similarity >= threshold:
                answer = self.answers[best_match_idx]
                logger.info(f"Found matching answer with similarity {best_similarity:.2f}")
                return answer
            else:
                logger.info(f"No good match found. Best similarity: {best_similarity:.2f}")
                return None
                
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            return None