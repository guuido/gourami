from abc import ABC, abstractmethod
from typing import Type
from pydantic import BaseModel, Field, ConfigDict

class BaseModelConfig(BaseModel):
    temperature: float = Field(default=0.7, ge=0, le=2.0)
    max_tokens: int = Field(default=1000, gt=0)
    
    model_config = ConfigDict(extra="allow") 

class ChatModel(ABC):
    @classmethod
    @abstractmethod
    def get_config_class(cls) -> Type[BaseModelConfig]:
        """Return the configuration class for this model"""
        pass

    @abstractmethod
    def predict(self, message: str, temperature: float = 0.7, max_tokens: int = 1000) -> str:
        """Process the user's message and return a response."""
        pass

