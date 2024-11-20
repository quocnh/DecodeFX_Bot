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
        self.logger = logging.getLogger(__name__)
        
        if not huggingface_token:
            self.logger.error("No Hugging Face token provided")
            raise ValueError("Hugging Face token is required")
        
        os.environ["HUGGINGFACE_TOKEN"] = huggingface_token
        
        self.logger.info("Loading sentence transformer model...")
        self.encoder = SentenceTransformer('vinai/phobert-base')
        
        try:
            self.logger.info("Loading Llama 2 model...")
            # Check for GPU availability
            if torch.cuda.is_available():
                self.logger.info("GPU detected, loading model with 8-bit quantization")
                model_kwargs = {
                    "torch_dtype": torch.float16,
                    "device_map": "auto",
                    "load_in_8bit": True
                }
            else:
                self.logger.info("No GPU detected, loading model in CPU mode")
                model_kwargs = {
                    "torch_dtype": torch.float32,
                    "low_cpu_mem_usage": True
                }

            # Load tokenizer
            self.llama_tokenizer = AutoTokenizer.from_pretrained(
                "meta-llama/Llama-2-7b-chat-hf",
                use_auth_token=huggingface_token
            )
            
            # Load model with appropriate settings
            self.llama_model = AutoModelForCausalLM.from_pretrained(
                "meta-llama/Llama-2-7b-chat-hf",
                use_auth_token=huggingface_token,
                **model_kwargs
            )
            
            self.logger.info("Llama 2 model loaded successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to load Llama 2: {str(e)}", exc_info=True)
            
            # Try loading a smaller model instead
            try:
                self.logger.info("Attempting to load smaller model (OPT-350M)...")
                self.llama_tokenizer = AutoTokenizer.from_pretrained("facebook/opt-350m")
                self.llama_model = AutoModelForCausalLM.from_pretrained(
                    "facebook/opt-350m",
                    torch_dtype=torch.float32,
                    low_cpu_mem_usage=True
                )
                self.logger.info("Loaded OPT-350M as fallback model")
            except Exception as fallback_e:
                self.logger.error(f"Failed to load fallback model: {str(fallback_e)}")
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
        if not self.llama_model or not self.llama_tokenizer:
            self.logger.error("Llama model or tokenizer not initialized")
            return None
            
        try:
            if system_prompt is None:
                system_prompt = """Bạn là trợ lý AI đa năng.
                Hãy trả lời câu hỏi một cách chuyên nghiệp.
                Với câu hỏi về Decode FX, hãy cung cấp thông tin chính xác.
                Với câu hỏi chung, hãy trả lời dựa trên kiến thức của bạn."""

            # Improved chat format
            chat_format = f"""<s>[INST] <<SYS>>
            {system_prompt}
            <</SYS>>
            
            Người dùng: {query} [/INST]
            Trợ lý:"""

            inputs = self.llama_tokenizer(chat_format, return_tensors="pt", padding=True)
            inputs = {k: v.to(self.llama_model.device) for k, v in inputs.items()}
            
            with torch.no_grad():
                outputs = self.llama_model.generate(
                    **inputs,
                    max_new_tokens=512,  # Changed from max_length
                    temperature=0.7,
                    top_p=0.9,
                    num_beams=4,
                    do_sample=True,
                    no_repeat_ngram_size=3,
                    early_stopping=True,
                    pad_token_id=self.llama_tokenizer.pad_token_id
                )
            
            response = self.llama_tokenizer.decode(outputs[0], skip_special_tokens=True)
            # Extract only the assistant's response
            response = response.split("Trợ lý:")[-1].strip()
            
            if not response:
                self.logger.warning("Empty response generated")
                return None
            
            self.logger.info(f"Generated response: {response}")    
            return response
        except Exception as e:
            self.logger.error(f"Llama 2 generation failed: {str(e)}")
            return None

    def get_best_response(self, query: str, qa_pairs: list) -> Tuple[str, float]:
        # Strategy 1:For Decode FX specific queries, try training data first
        self.logger.info("Attempting to find response in training data...")
        if any(keyword in query.lower() for keyword in ['decode', 'fx', 'trading', 'account']):
            response, confidence = self.get_training_response(query, qa_pairs)
            if response and confidence >= 0.7:
                return response, confidence
        
        # Strategy 2: For general queries or if training data doesn't match well, try Llama
        self.logger.info("Attempting to generate response with Llama 2...")
        llama_response = self.get_llama_response(query)
        if llama_response:
            self.logger.info("Successfully generated response with Llama 2")
            return llama_response, 0.5
        
        # Strategy 3: If everything fails, try training data as last resort
        response, confidence = self.get_training_response(query, qa_pairs)
        if response:
            return response, confidence
        
        self.logger.warning("No suitable response found, using default response")
        default_response = """
        Xin lỗi, tôi không thể trả lời câu hỏi này.
        Vui lòng:
        • Diễn đạt lại câu hỏi một cách rõ ràng hơn
        • Liên hệ với bộ phận hỗ trợ khách hàng qua email support@decode.com
        • Hoặc gọi hotline: 1900-xxx-xxx
        """    
        return default_response, 0.0

    # def get_best_response(self, query: str, qa_pairs: list) -> Tuple[str, float]:
    #     """
    #     Try different strategies to get the best response
    #     """
    #     # Strategy 1: Try training data
    #     self.logger.info("Attempting to find response in training data...")
    #     response, confidence = self.get_training_response(query, qa_pairs)
    #     if response and confidence >= 0.7:  # Added confidence threshold check
    #         self.logger.info(f"Found matching response in training data with confidence {confidence}")
    #         return response, confidence

    #     # Strategy 2: Try Llama 2
    #     self.logger.info("Attempting to generate response with Llama 2...")
    #     response = self.get_llama_response(query)
    #     if response:
    #         self.logger.info("Successfully generated response with Llama 2")
    #         return response, 0.5

    #     # Strategy 3: Default response
    #     self.logger.warning("No suitable response found, using default response")
    #     default_response = """
    #     Xin lỗi, tôi không thể trả lời câu hỏi này.
    #     Vui lòng:
    #     • Diễn đạt lại câu hỏi một cách rõ ràng hơn
    #     • Liên hệ với bộ phận hỗ trợ khách hàng qua email support@decode.com
    #     • Hoặc gọi hotline: 1900-xxx-xxx
    #     """
    #     return default_response, 0.0