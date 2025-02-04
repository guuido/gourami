from enum import Enum
import json
import os
from typing import Any, Dict, Optional
from pydantic import Field, ConfigDict
from pydantic_settings import BaseSettings

class ExecutionStrategy(str, Enum):
    THREAD_POOL = "thread"
    PROCESS_POOL = "process"

class Settings(BaseSettings):
    HOST: str = Field(default="0.0.0.0")
    PORT: int = Field(default=5000)
    DISABLE_LOGGING: bool = Field(default=True)
    MODEL_TYPE: str = Field(default="huggingface")
    EXECUTION_STRATEGY: ExecutionStrategy = Field(default=ExecutionStrategy.THREAD_POOL)
    POOL_SIZE: int = Field(default=4)

    model_params: Dict[str, Any] = Field(
        default_factory=dict,
        json_schema_extra={"env_serializer": lambda v: json.dumps(v) if v else "{}"}
    )

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="GOURAMI_",
        extra='ignore'
    )


def configure_settings(params: Optional[Dict[str, Any]] = None, config_path: Optional[str] = None) -> Settings:
    """
    Configure settings by setting environment variables.
    """
    settings_dict = {}
    
    # Load config file if specified
    if config_path:
        try:
            with open(config_path, 'r') as f:
                config_data = json.load(f)
                settings_dict.update(config_data)
        except Exception as e:
            print(f"Error loading config file: {e}")

    # Apply CLI overrides
    if params:
        settings_dict.update(params)
    
    # Set environment variables with prefix
    for key, value in settings_dict.items():
        if value is not None:
            env_key = f"GOURAMI_{key.upper()}"

            if isinstance(value, dict):
                value = json.dumps(value)
            os.environ[env_key] = str(value)

    global _settings_instance
    _settings_instance = Settings()

    return _settings_instance

_settings_instance: Optional[Settings] = None

def get_settings():
    global _settings_instance
    if not _settings_instance:
        _settings_instance = Settings()
        return _settings_instance
    else: 
        return _settings_instance
