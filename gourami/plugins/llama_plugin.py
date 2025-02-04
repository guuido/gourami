from typing import Optional, Type
from gourami.core.model import BaseModelConfig, ChatModel
from pydantic import Field

class LlamaConfig(BaseModelConfig):
    model_name: str = Field(default="meta-llama/Llama-2-7b-chat-hf")
    device: str = Field(default="cuda")
    do_sample: bool = Field(default=True)
    top_p: float = Field(default=0.9, ge=0, le=1)
    top_k: int = Field(default=50, ge=0)
    torch_dtype: str = Field(default="float16")
    low_cpu_mem_usage: bool = Field(default=True)
    hf_token: Optional[str] = Field(default=None)

class LlamaModel(ChatModel):
    @classmethod
    def get_config_class(cls) -> Type[BaseModelConfig]:
        return LlamaConfig

    def __init__(self, config: LlamaConfig):
        from transformers import AutoModelForCausalLM, AutoTokenizer
        import torch
        
        if config.hf_token:
            self.tokenizer = AutoTokenizer.from_pretrained(config.model_name,token=config.hf_token)
        else:
            self.tokenizer = AutoTokenizer.from_pretrained(config.model_name)
        
        model_kwargs = {
            'device_map': 'auto',
            'torch_dtype': getattr(torch, config.torch_dtype),
            'low_cpu_mem_usage': config.low_cpu_mem_usage
        }

        if config.hf_token:
            model_kwargs.update({"token":config.hf_token})
        
        self.model = AutoModelForCausalLM.from_pretrained(
            config.model_name, 
            **model_kwargs
        )
        
        self.tokenizer.pad_token = self.tokenizer.eos_token
        self.config = config
    
    def predict(self, message: str) -> str:
        import torch
        
        inputs = self.tokenizer(
            message, 
            return_tensors="pt", 
            add_special_tokens=True
        ).to(self.model.device)
        
        generate_kwargs = {k: v for k, v in self.config.dict().items() 
                         if v is not None and k not in ['model_name', 'device', 'torch_dtype', 'low_cpu_mem_usage', 'hf_token', 'max_tokens']}
        
        with torch.no_grad():
            outputs = self.model.generate(
                inputs.input_ids, 
                **generate_kwargs
            )
        
        response = self.tokenizer.decode(
            outputs[0][inputs.input_ids.shape[1]:], 
            skip_special_tokens=True
        ).strip()
        
        return response
