from typing import Optional, Type
from gourami.core.model import BaseModelConfig, ChatModel
from pydantic import Field

class AnthropicConfig(BaseModelConfig):
    api_key: Optional[str] = Field(default=None)
    model_name: str = Field(default="claude-3-haiku-20240307")
    top_p: Optional[float] = Field(default=None, ge=0, le=1)
    top_k: Optional[int] = Field(default=None, ge=0)

class AnthropicModel(ChatModel):
    @classmethod
    def get_config_class(cls) -> Type[BaseModelConfig]:
        return AnthropicConfig

    def __init__(self, config: AnthropicConfig):
        import anthropic
        
        api_key = config.api_key
        if not api_key:
            raise ValueError("Anthropic API key is required")
        
        self.client = anthropic.Anthropic(api_key=api_key)
        self.config = config
    
    def predict(self, message: str) -> str:
        kwargs = {k: v for k, v in self.config.dict().items() 
                 if v is not None and k not in ['api_key']}
        
        response = self.client.messages.create(
            model=self.config.model_name,
            messages=[{"role": "user", "content": message}],
            **kwargs
        )
        return response.content[0].text