"""
Custom LangChain LLM wrapper for Sarvam AI API
"""
from typing import Any, List, Optional
from langchain_core.language_models.llms import LLM
from langchain_core.callbacks.manager import CallbackManagerForLLMRun
import requests
import os

class SarvamLLM(LLM):
    """
    Custom LLM implementation for Sarvam AI
    """
    
    api_key: str = ""
    api_url: str = "https://api.sarvam.ai/v1/chat/completions"
    model: str = "sarvam-2b"
    temperature: float = 0.7
    max_tokens: int = 2000
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.api_key = os.getenv("SARVAM_API_KEY", "")
        self.api_url = os.getenv("SARVAM_API_URL", self.api_url)
        self.model = os.getenv("SARVAM_MODEL", self.model)
    
    @property
    def _llm_type(self) -> str:
        return "sarvam"
    
    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """
        Call Sarvam AI API
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }
        
        try:
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            
            result = response.json()
            
            # Extract response based on Sarvam AI response format
            if "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"]
            elif "response" in result:
                return result["response"]
            else:
                return str(result)
                
        except requests.exceptions.RequestException as e:
            raise Exception(f"Sarvam AI API error: {str(e)}")
    
    @property
    def _identifying_params(self):
        """Get the identifying parameters."""
        return {
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }
