from typing import Optional, Type
from gourami.core.model import BaseModelConfig, ChatModel
from pydantic import Field

class OpenAIConfig(BaseModelConfig):
    api_key: Optional[str] = Field(default=None)
    model_name: str = Field(default="gpt-3.5-turbo")
    presence_penalty: Optional[float] = Field(default=None, ge=-2.0, le=2.0)
    frequency_penalty: Optional[float] = Field(default=None, ge=-2.0, le=2.0)


class OpenAIModel(ChatModel):
    @classmethod
    def get_config_class(cls) -> Type[BaseModelConfig]:
        return OpenAIConfig

    def __init__(self, config: OpenAIConfig):
        import openai
        
        api_key = config.api_key
        if not api_key:
            raise ValueError("OpenAI API key is required.")
        
        self.client = openai.OpenAI(api_key=api_key)
        self.config = config
    
    def predict(self, message: str) -> str:
        kwargs = {k: v for k, v in self.config.dict().items() 
                 if v is not None and k not in ['api_key', 'model_name']}
        
        response = self.client.chat.completions.create(
            model=self.config.model_name,
            messages=[{"role": "user", "content": message}],
            **kwargs
        )
        return response.choices[0].message.content