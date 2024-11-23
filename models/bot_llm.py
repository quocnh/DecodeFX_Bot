# models/bot_llm.py
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import random
from config import logger

class BotLLMModel:
    def __init__(self, dataset_path):
        logger.info("Initializing BotLLMModel")
        try:
            self.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
            self.questions, self.answers = self._load_md_dataset(dataset_path)
            self.question_embeddings = self.model.encode(self.questions)
            logger.info(f"Successfully loaded dataset with {len(self.questions)} QA pairs")
        except Exception as e:
            logger.error(f"Error initializing BotLLMModel: {str(e)}")
            raise

    def _extract_qa_from_block(self, block):
        """Extract question and answer from a QA block"""
        try:
            lines = block.strip().split('\n')
            question = None
            answer = None
            
            for line in lines:
                line = line.strip()
                if line.startswith('KHÁCH_HÀNG:'):
                    # Extract question text between quotes
                    question = line.split('"')[1] if '"' in line else line.split('KHÁCH_HÀNG:')[1].strip()
                elif line.startswith('TRẢ_LỜI:'):
                    # Extract answer text between quotes
                    answer = line.split('"')[1] if '"' in line else line.split('TRẢ_LỜI:')[1].strip()
            
            return question, answer
        except Exception as e:
            logger.error(f"Error parsing QA block: {str(e)}")
            return None, None

    def _load_md_dataset(self, file_path):
        """
        Load Q&A pairs from markdown file.
        """
        questions = []
        answers = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                
            # Split content into QA blocks
            qa_blocks = content.split('\n\n')  # Assuming blocks are separated by double newlines
            
            for block in qa_blocks:
                if not block.strip():
                    continue
                    
                question, answer = self._extract_qa_from_block(block)
                if question and answer:
                    questions.append(question)
                    answers.append(answer)
                    logger.debug(f"Loaded Q: {question[:50]}...")
                    
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
        suitable_questions = [q for q in self.questions if 10 <= len(q) <= 100]
        if len(suitable_questions) > n:
            samples = random.sample(suitable_questions, n)
        else:
            samples = suitable_questions
        return samples

    def find_best_answer(self, query, threshold=0.7):
        try:
            query = query.strip()
            logger.info(f"Processing query: {query}")

            # Check if query is too general
            if self._is_general_query(query):
                sample_questions = self._get_sample_questions()
                response = "Xin chào! Bạn có thể hỏi tôi những câu hỏi như:\n\n"
                for i, question in enumerate(sample_questions, 1):
                    response += f"{i}. {question}\n"
                logger.info("Returning sample questions for general query")
                return response

            # Normal processing for specific queries
            query_embedding = self.model.encode([query])
            similarities = cosine_similarity(query_embedding, self.question_embeddings)[0]
            best_match_idx = np.argmax(similarities)
            best_similarity = similarities[best_match_idx]
            
            logger.debug(f"Best match similarity: {best_similarity}")
            logger.debug(f"Best matching question: {self.questions[best_match_idx]}")
            
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