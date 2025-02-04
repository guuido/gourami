from typing import Optional, Type
from gourami.core.model import BaseModelConfig, ChatModel
from pydantic import Field

class MixtralConfig(BaseModelConfig):
    model_name: str = Field(default="mistralai/Mixtral-8x7B-Instruct-v0.1")
    device: str = Field(default="cuda")
    do_sample: bool = Field(default=True)
    top_p: float = Field(default=0.9, ge=0, le=1)
    top_k: int = Field(default=50, ge=0)
    torch_dtype: str = Field(default="float16")
    low_cpu_mem_usage: bool = Field(default=True)
    hf_token: Optional[str] = Field(default=None)

class MixtralModel(ChatModel):
    @classmethod
    def get_config_class(cls) -> Type[BaseModelConfig]:
        return MixtralConfig

    def __init__(self, config: MixtralConfig):
        from transformers import AutoModelForCausalLM, AutoTokenizer
        import torch

        if config.hf_token:
            self.tokenizer = AutoTokenizer.from_pretrained(config.model_name,token=config.hf_token)
        else:
            self.tokenizer = AutoTokenizer.from_pretrained(config.model_name)
        
        # Add chat template specifically for Mixtral
        self.tokenizer.chat_template = "{% if messages[0]['role'] == 'system' %}{% set loop_messages = messages[1:] %}{% else %}{% set loop_messages = messages %}{% endif %}{{ bos_token }}{% for message in loop_messages %}{% if message['role'] == 'user' %}{{ '[INST] ' + message['content'] + ' [/INST]' }}{% elif message['role'] == 'assistant' %}{{ message['content'] + eos_token }}{% endif %}{% endfor %}"
        
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
        
        messages = [{"role": "user", "content": message}]
        inputs = self.tokenizer.apply_chat_template(
            messages, 
            return_tensors="pt", 
            add_generation_prompt=True
        ).to(self.model.device)
        
        generate_kwargs = {k: v for k, v in self.config.dict().items() 
                         if v is not None and k not in ['model_name', 'device', 'torch_dtype', 'low_cpu_mem_usage', 'hf_token']}
        
        with torch.no_grad():
            outputs = self.model.generate(
                inputs, 
                **generate_kwargs
            )
        
        response = self.tokenizer.decode(
            outputs[0][inputs.shape[1]:], 
            skip_special_tokens=True
        ).strip()
        
        return response