from typing import Optional, Type
from gourami.core.model import BaseModelConfig, ChatModel
from pydantic import Field

class HuggingFaceConfig(BaseModelConfig):
    model_name: str = Field(default="facebook/opt-350m")
    repetition_penalty: float = Field(default=1.2, ge=0)
    top_p: float = Field(default=0.9, ge=0, le=1.0)
    top_k: int = Field(default=50, ge=0)
    num_beams: int = Field(default=1, ge=1)
    device: str = Field(default="cpu")
    hf_token: Optional[str] = Field(default=None)

class HuggingFaceModel(ChatModel):
    @classmethod
    def get_config_class(cls) -> Type[BaseModelConfig]:
        return HuggingFaceConfig

    def __init__(self, config: HuggingFaceConfig):
        self.config = config
        from transformers import AutoModelForCausalLM, AutoTokenizer

        if config.hf_token:
            self.tokenizer = AutoTokenizer.from_pretrained(config.model_name,token=config.hf_token)
            self.model = AutoModelForCausalLM.from_pretrained(config.model_name,token=config.hf_token)
        else:
            self.tokenizer = AutoTokenizer.from_pretrained(config.model_name)
            self.model = AutoModelForCausalLM.from_pretrained(config.model_name)
        
        self.model.to(config.device)
    
    def predict(self, message: str) -> str:
        inputs = self.tokenizer(message, return_tensors="pt").to(self.config.device)
        
        outputs = self.model.generate(
            **inputs,
            max_length=len(inputs.input_ids[0]) + self.config.max_tokens,
            temperature=self.config.temperature,
            repetition_penalty=self.config.repetition_penalty,
            top_p=self.config.top_p,
            top_k=self.config.top_k,
            num_beams=self.config.num_beams,
        )
        
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)