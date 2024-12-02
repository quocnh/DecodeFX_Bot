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
        """
        Load Q&A pairs from markdown file.
        """
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
        suitable_questions = [q for q in self.questions if 10 <= len(q) <= 100]
        if len(suitable_questions) > n:
            samples = random.sample(suitable_questions, n)
        else:
            samples = suitable_questions
        return samples

    def find_best_answer(self, query, threshold=0.6):
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