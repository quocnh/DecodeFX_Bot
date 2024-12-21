from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from text_processing_helper import TextProcessor
import numpy as np
from typing import List, Dict, Tuple
import re

class EnhancedBotModel:
    def __init__(self, dataset_path):
        self.base_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        self.load_dataset(dataset_path)
        self.context_mapping = self._build_context_mapping()
        self.text_processor = TextProcessor()
        self.last_suggestions = {}
        
    def load_dataset(self, dataset_path):
        # Original dataset loading code remains the same
        self.qa_pairs = []
        self.topics = set()
        self.entities = {}
        
        with open(dataset_path, 'r', encoding='utf-8') as file:
            content = file.read()
            sections = content.split('##')
            
            for section in sections:
                if not section.strip():
                    continue
                    
                # Extract topic from section header
                topic = section.split('\n')[0].strip()
                self.topics.add(topic)
                
                # Extract QA pairs and build knowledge base
                qa_blocks = re.findall(r'KHÁCH_HÀNG:.*?(?=KHÁCH_HÀNG:|$)', section, re.DOTALL)
                for block in qa_blocks:
                    qa_pair = self._parse_qa_block(block)
                    if qa_pair:
                        self.qa_pairs.append(qa_pair)
                        self._extract_entities(qa_pair, topic)

    def _parse_qa_block(self, block: str) -> Dict:
        """Parse a QA block into structured data with context"""
        lines = block.strip().split('\n')
        qa_data = {
            'question': '',
            'answer': '',
            'context': '',
            'labels': [],
            'priority': ''
        }
        
        current_field = None
        for line in lines:
            line = line.strip()
            if line.startswith('KHÁCH_HÀNG:'):
                current_field = 'question'
                qa_data['question'] = self._extract_quoted_text(line)
            elif line.startswith('BỐI_CẢNH:'):
                current_field = 'context'
                qa_data['context'] = self._extract_quoted_text(line)
            elif line.startswith('TRẢ_LỜI:'):
                current_field = 'answer'
                qa_data['answer'] = self._extract_quoted_text(line)
            elif line.startswith('NHÃN:'):
                qa_data['labels'] = self._extract_labels(line)
            elif line.startswith('ĐỘ_ƯU_TIÊN:'):
                qa_data['priority'] = line.split(':')[1].strip().strip('"')
            elif current_field == 'answer' and line:
                qa_data['answer'] += ' ' + line.strip('"')
                
        return qa_data if qa_data['question'] and qa_data['answer'] else None

    def _build_context_mapping(self) -> Dict:
        """Build a mapping of contexts and their related information"""
        context_map = {}
        
        for qa_pair in self.qa_pairs:
            context = qa_pair['context']
            if context not in context_map:
                context_map[context] = {
                    'related_qa': [],
                    'labels': set(),
                    'priority': set()
                }
            
            context_map[context]['related_qa'].append({
                'question': qa_pair['question'],
                'answer': qa_pair['answer']
            })
            context_map[context]['labels'].update(qa_pair['labels'])
            context_map[context]['priority'].add(qa_pair['priority'])
            
        return context_map

    def _extract_entities(self, qa_pair: Dict, topic: str):
        """Extract and store important entities and their relationships"""
        # Extract entities from question and answer
        text = f"{qa_pair['question']} {qa_pair['answer']}"
        
        # Define entity patterns (add more as needed)
        patterns = {
            'product': r'(MT4|ECN|PAMM|MAM|VPS)',
            'service': r'(KYC|BONUS|FREESWAP|COMMISSION)',
            'amount': r'(\d+(?:k|K|\$)?)',
            'percentage': r'(\d+(?:\.\d+)?%)',
            'time': r'(\d{1,2}(?:h|giờ)|(?:sáng|chiều|tối))'
        }
        
        for entity_type, pattern in patterns.items():
            matches = re.findall(pattern, text)
            if matches:
                if entity_type not in self.entities:
                    self.entities[entity_type] = {}
                
                for match in matches:
                    if match not in self.entities[entity_type]:
                        self.entities[entity_type][match] = {
                            'topics': set(),
                            'contexts': set()
                        }
                    self.entities[entity_type][match]['topics'].add(topic)
                    self.entities[entity_type][match]['contexts'].add(qa_pair['context'])

    def find_best_answer(self, query: str, chat_id: str = None, context: str = None, previous_response: str = None) -> str:
        # Check if this is a confirmation of a previous suggestion
        if chat_id and chat_id in self.last_suggestions:
            confirmation_words = {
                'đúng', 'yes', 'phải', 'ừ', 'đúng rồi', 'ok', 
                'uhm', 'uh', 'ừm', 'um', 'vâng', 'vang', 
                'dạ', 'da', 'uk', 'đúng vậy', 'chính xác',
                'y', 'đúng ạ', 'vâng ạ', 'dạ đúng', 'dạ phải',
                'đúng đó', 'phải rồi', 'ứ', 'ừa', 'ua'
            }
            if any(word.lower() in query.lower() for word in confirmation_words):
                answer = self.last_suggestions[chat_id]['answer']
                del self.last_suggestions[chat_id]  # Clear the suggestion
                return answer

        # Process and fix the query
        fixed_query, needs_confirmation, original = self.text_processor.fix_question(query)
        
        # If the question needs confirmation, store the potential answer and ask for confirmation
        if needs_confirmation:
            # Try to find the best matching question
            similar_q, similarity = self.text_processor.find_similar_question(
                fixed_query, 
                [qa['question'] for qa in self.qa_pairs]
            )
            
            if similarity > 0.6:  # Threshold for suggesting
                for qa in self.qa_pairs:
                    if qa['question'] == similar_q:
                        if chat_id:
                            self.last_suggestions[chat_id] = {
                                'answer': qa['answer'],
                                'original_query': original
                            }
                        return f"Có phải bạn muốn hỏi: '{similar_q}'?"
        """Enhanced answer finding with reasoning capabilities"""
        # 1. Direct matching attempt
        direct_match = self._find_direct_match(query)
        if direct_match:
            return direct_match

        # 2. Context-based reasoning
        context_match = self._reason_from_context(query)
        if context_match:
            return context_match

        # 3. Entity-based reasoning
        entity_match = self._reason_from_entities(query)
        if entity_match:
            return entity_match

        # 4. Topic-based synthesis
        synthesized_answer = self._synthesize_answer(query)
        if synthesized_answer:
            return synthesized_answer

        return "Xin lỗi, tôi không có đủ thông tin để trả lời câu hỏi này. Vui lòng liên hệ CSKH để được hỗ trợ thêm."

    def _find_direct_match(self, query: str) -> str:
        """Try to find a direct match using semantic similarity"""
        query_embedding = self.base_model.encode([query])
        best_match = None
        best_similarity = 0
        
        for qa_pair in self.qa_pairs:
            question_embedding = self.base_model.encode([qa_pair['question']])
            similarity = cosine_similarity(query_embedding, question_embedding)[0][0]
            
            if similarity > best_similarity:
                best_similarity = similarity
                best_match = qa_pair
        
        if best_similarity > 0.8:  # High confidence threshold
            return best_match['answer']
        return None

    def _reason_from_context(self, query: str) -> str:
        """Attempt to reason based on similar contexts"""
        relevant_contexts = []
        query_embedding = self.base_model.encode([query])[0]
        
        # Find relevant contexts
        for context, data in self.context_mapping.items():
            context_embedding = self.base_model.encode([context])[0]
            similarity = cosine_similarity([query_embedding], [context_embedding])[0][0]
            
            if similarity > 0.6:  # Context relevance threshold
                relevant_contexts.append((context, similarity, data))
        
        if relevant_contexts:
            # Sort by similarity and combine information
            relevant_contexts.sort(key=lambda x: x[1], reverse=True)
            answer_parts = []
            
            for context, _, data in relevant_contexts[:2]:  # Use top 2 most relevant contexts
                # Extract key information from related QA pairs
                key_points = set()
                for qa in data['related_qa']:
                    # Extract key phrases or sentences
                    sentences = qa['answer'].split('.')
                    for sentence in sentences:
                        if any(label in sentence.lower() for label in data['labels']):
                            key_points.add(sentence.strip())
                
                # Combine key points into coherent answer
                if key_points:
                    answer_parts.extend(list(key_points))
            
            if answer_parts:
                return " ".join(answer_parts)
        
        return None

    def _reason_from_entities(self, query: str) -> str:
        """Reason based on recognized entities in the query"""
        # Extract entities from query
        found_entities = {}
        for entity_type, patterns in self.entities.items():
            for entity, data in patterns.items():
                if entity.lower() in query.lower():
                    if entity_type not in found_entities:
                        found_entities[entity_type] = []
                    found_entities[entity_type].append((entity, data))
        
        if found_entities:
            # Construct answer based on entity relationships
            answer_parts = []
            
            for entity_type, entities in found_entities.items():
                for entity, data in entities:
                    # Find related QA pairs
                    related_qa = []
                    for qa_pair in self.qa_pairs:
                        if any(context in data['contexts'] for context in [qa_pair['context']]):
                            related_qa.append(qa_pair)
                    
                    # Extract relevant information
                    if related_qa:
                        relevant_info = self._extract_relevant_info(entity, related_qa)
                        if relevant_info:
                            answer_parts.append(relevant_info)
            
            if answer_parts:
                return " ".join(answer_parts)
        
        return None

    def _synthesize_answer(self, query: str) -> str:
        """Synthesize an answer by combining relevant information from multiple sources"""
        # Identify topics in query
        query_embedding = self.base_model.encode([query])[0]
        relevant_topics = []
        
        for topic in self.topics:
            topic_embedding = self.base_model.encode([topic])[0]
            similarity = cosine_similarity([query_embedding], [topic_embedding])[0][0]
            if similarity > 0.5:
                relevant_topics.append((topic, similarity))
        
        if relevant_topics:
            # Sort topics by relevance
            relevant_topics.sort(key=lambda x: x[1], reverse=True)
            
            # Collect relevant information from each topic
            answer_components = []
            covered_points = set()
            
            for topic, _ in relevant_topics[:2]:  # Use top 2 most relevant topics
                topic_qa_pairs = [qa for qa in self.qa_pairs if qa.get('topic') == topic]
                
                for qa_pair in topic_qa_pairs:
                    # Extract key points that haven't been covered
                    points = self._extract_key_points(qa_pair['answer'])
                    new_points = points - covered_points
                    
                    if new_points:
                        answer_components.extend(list(new_points))
                        covered_points.update(new_points)
            
            if answer_components:
                return self._format_synthesized_answer(answer_components)
        
        return None

    def _extract_key_points(self, text: str) -> set:
        """Extract key points from text"""
        sentences = text.split('.')
        return set(sent.strip() for sent in sentences if sent.strip())

    def _format_synthesized_answer(self, components: List[str]) -> str:
        """Format multiple components into a coherent answer"""
        if not components:
            return None
            
        # Group related points
        grouped_points = []
        current_group = []
        
        for point in components:
            if not current_group:
                current_group.append(point)
            else:
                # Check if point is related to current group
                current_text = ' '.join(current_group)
                point_embedding = self.base_model.encode([point])[0]
                group_embedding = self.base_model.encode([current_text])[0]
                
                similarity = cosine_similarity([point_embedding], [group_embedding])[0][0]
                
                if similarity > 0.6:  # Related point threshold
                    current_group.append(point)
                else:
                    grouped_points.append(current_group)
                    current_group = [point]
        
        if current_group:
            grouped_points.append(current_group)
        
        # Format answer
        formatted_answer = ""
        for group in grouped_points:
            formatted_answer += " ".join(group) + "\n\n"
        
        return formatted_answer.strip()

    @staticmethod
    def _extract_quoted_text(line: str) -> str:
        """Extract text between quotes"""
        match = re.search(r'"([^"]*)"', line)
        return match.group(1) if match else ""

    @staticmethod
    def _extract_labels(line: str) -> List[str]:
        """Extract labels from label line"""
        match = re.search(r'\[(.*?)\]', line)
        if match:
            return [label.strip().strip('"') for label in match.group(1).split(',')]
        return []

    def _extract_relevant_info(self, entity: str, qa_pairs: List[Dict]) -> str:
        """Extract relevant information about an entity from QA pairs"""
        relevant_sentences = []
        
        for qa_pair in qa_pairs:
            sentences = qa_pair['answer'].split('.')
            for sentence in sentences:
                if entity.lower() in sentence.lower():
                    relevant_sentences.append(sentence.strip())
        
        return ' '.join(relevant_sentences) if relevant_sentences else None