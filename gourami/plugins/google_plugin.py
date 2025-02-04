from typing import Optional, Type
from gourami.core.model import BaseModelConfig, ChatModel
from pydantic import Field

class GoogleConfig(BaseModelConfig):
    api_key: Optional[str] = Field(default=None)
    model_name: str = Field(default="gemini-pro")
    candidate_count: Optional[int] = Field(default=None, ge=1)
    top_p: Optional[float] = Field(default=None, ge=0, le=1)
    top_k: Optional[int] = Field(default=None, ge=0)

class GoogleModel(ChatModel):
    @classmethod
    def get_config_class(cls) -> Type[BaseModelConfig]:
        return GoogleConfig

    def __init__(self, config: GoogleConfig):
        import google.generativeai as genai
        
        api_key = config.api_key
        if not api_key:
            raise ValueError("Google API key is required.")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(config.model_name)
        self.config = config
    
    def predict(self, message: str) -> str:
        generation_config = {k: v for k, v in self.config.dict().items() 
                           if v is not None and k not in ['api_key', 'model_name']}
        
        response = self.model.generate_content(
            message, 
            generation_config=generation_config
        )
        return response.text