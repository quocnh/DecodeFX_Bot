from typing import Tuple, Optional
import os
from transformers import AutoModelForCausalLM, AutoTokenizer
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import torch
import logging

class LanguageModelService:
    def __init__(self, huggingface_token: str):
        """
        Initialize language models for response generation
        
        Args:
            huggingface_token (str): HuggingFace API token for accessing models
        """
        self.logger = logging.getLogger(__name__)
        
        # Set HuggingFace token
        os.environ["HUGGINGFACE_TOKEN"] = huggingface_token
        
        # Initialize sentence transformer for semantic matching
        self.logger.info("Loading sentence transformer model...")
        self.encoder = SentenceTransformer('vinai/phobert-base')
        
        # Initialize Llama 2 for general text generation
        try:
            self.logger.info("Loading Llama 2 model...")
            self.llama_tokenizer = AutoTokenizer.from_pretrained(
                "meta-llama/Llama-2-7b-chat-hf",
                use_auth_token=huggingface_token
            )
            self.llama_model = AutoModelForCausalLM.from_pretrained(
                "meta-llama/Llama-2-7b-chat-hf",
                use_auth_token=huggingface_token,
                torch_dtype=torch.float16,
                device_map="auto"
            )
            self.logger.info("Llama 2 model loaded successfully")
        except Exception as e:
            self.logger.error(f"Failed to load Llama 2 model: {e}")
            self.llama_model = None
            self.llama_tokenizer = None

    def get_training_response(self, query: str, qa_pairs: list, threshold: float = 0.7) -> Tuple[str, float]:
        """
        Try to find a response from training data
        """
        query_embedding = self.encoder.encode([query])
        question_embeddings = self.encoder.encode([pair['question'] for pair in qa_pairs])
        similarities = cosine_similarity(query_embedding, question_embeddings)[0]
        
        best_idx = np.argmax(similarities)
        best_similarity = similarities[best_idx]
        
        if best_similarity >= threshold:
            return (qa_pairs[best_idx]['answer'], best_similarity)
        return (None, best_similarity)

    def get_llama_response(self, query: str, system_prompt: str = None) -> Optional[str]:
        """
        Generate a response using Llama 2
        """
        if not self.llama_model or not self.llama_tokenizer:
            return None
            
        try:
            if system_prompt is None:
                system_prompt = """You are a helpful customer service assistant for Decode FX. 
                Respond in Vietnamese. Be concise and professional. 
                If you're not sure about specific Decode FX details, provide general guidance."""

            chat_format = f"""<s>[INST] <<SYS>>
            {system_prompt}
            <</SYS>>

            {query} [/INST]"""

            inputs = self.llama_tokenizer(chat_format, return_tensors="pt").to(self.llama_model.device)
            
            outputs = self.llama_model.generate(
                inputs.input_ids,
                max_length=512,
                temperature=0.7,
                top_p=0.9,
                num_beams=4,
                do_sample=True,
                no_repeat_ngram_size=3,
                early_stopping=True
            )
            
            response = self.llama_tokenizer.decode(outputs[0], skip_special_tokens=True)
            response = response.split("[/INST]")[-1].strip()
            
            return response
        except Exception as e:
            self.logger.error(f"Llama 2 generation failed: {e}")
            return None

    def get_best_response(self, query: str, qa_pairs: list) -> Tuple[str, float]:
        """
        Try different strategies to get the best response
        """
        # Strategy 1: Try training data
        self.logger.info("Attempting to find response in training data...")
        response, confidence = self.get_training_response(query, qa_pairs)
        if response:
            self.logger.info(f"Found matching response in training data with confidence {confidence}")
            return response, confidence

        # Strategy 2: Try Llama 2
        self.logger.info("Attempting to generate response with Llama 2...")
        response = self.get_llama_response(query)
        if response:
            self.logger.info("Successfully generated response with Llama 2")
            return response, 0.5

        # Strategy 3: Default response
        self.logger.warning("No suitable response found, using default response")
        default_response = """
        Xin lỗi, tôi không thể trả lời câu hỏi này.
        Vui lòng:
        • Diễn đạt lại câu hỏi một cách rõ ràng hơn
        • Liên hệ với bộ phận hỗ trợ khách hàng qua email support@decode.com
        • Hoặc gọi hotline: 1900-xxx-xxx
        """
        return default_response, 0.0