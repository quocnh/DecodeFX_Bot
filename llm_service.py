from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import logging
from typing import Optional
from config import Config

class LLMService:
    def __init__(self, model_name: str = Config.LLM_MODEL, 
                 token: str = Config.HUGGINGFACE_TOKEN):
        self.logger = logging.getLogger(__name__)
        
        try:
            # Initialize tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                model_name,
                use_auth_token=token,
                padding_side="left",
                truncation_side="left"
            )
            self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # Initialize model
            device_map = "auto" if torch.cuda.is_available() else "cpu"
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                use_auth_token=token,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                device_map=device_map,
                load_in_8bit=torch.cuda.is_available()
            )
            
            self.logger.info(f"LLM initialized successfully on {device_map}")
            
        except Exception as e:
            self.logger.error(f"Error initializing LLM: {str(e)}")
            raise

    def generate_response(self, query: str, system_prompt: str = Config.SYSTEM_PROMPT) -> Optional[str]:
        """Generate response using LLM"""
        try:
            # Format prompt
            prompt = f"""<s>[INST] <<SYS>>
            {system_prompt}
            <</SYS>>
            
            Người dùng: {query} [/INST]
            Trợ lý:"""
            
            # Tokenize
            inputs = self.tokenizer(
                prompt,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=512,
                return_attention_mask=True
            )
            
            # Move inputs to model's device
            inputs = {k: v.to(self.model.device) for k, v in inputs.items()}
            
            # Generate
            with torch.no_grad():
                outputs = self.model.generate(
                    input_ids=inputs.input_ids,
                    attention_mask=inputs.attention_mask,
                    max_new_tokens=512,
                    temperature=0.7,
                    top_p=0.9,
                    do_sample=True,
                    pad_token_id=self.tokenizer.pad_token_id,
                    eos_token_id=self.tokenizer.eos_token_id
                )
                
            # Decode response
            response = self.tokenizer.decode(
                outputs[0],
                skip_special_tokens=True,
                clean_up_tokenization_spaces=True
            )
            
            # Extract assistant's response
            response = response.split("Trợ lý:")[-1].strip()
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error generating response: {str(e)}")
            return None