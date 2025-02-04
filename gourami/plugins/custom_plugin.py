import os
import importlib.util
import sys
from pathlib import Path
from typing import Optional
from gourami.core.model import ChatModel

class CustomModelLoader:
    """
    Manages loading of custom model plugins from a designated directory.
    """
    DEFAULT_PLUGIN_DIR = os.path.expanduser("~/.gourami/plugins")

    @classmethod
    def ensure_plugin_dir(cls) -> str:
        """
        Ensure the custom plugins directory exists.
        
        Returns:
            str: Path to the custom plugins directory
        """
        os.makedirs(cls.DEFAULT_PLUGIN_DIR, exist_ok=True)
        
        # Create a sample template if no plugins exist
        template_path = os.path.join(cls.DEFAULT_PLUGIN_DIR, 'custom_model_template.py')
        if not os.path.exists(template_path):
            with open(template_path, 'w') as f:
                f.write("""from gourami.core.model import ChatModel

class CustomChatModel(ChatModel):
    def predict(self, message: str, **kwargs) -> str:
        \"\"\"
        Implement your custom model's prediction logic here.
        
        Args:
            message (str): The input message to process
            **kwargs: Additional generation parameters
        
        Returns:
            str: The model's response
        \"\"\"
        # Example implementation
        return f"Custom model response to: {message}"
""")
        
        return cls.DEFAULT_PLUGIN_DIR

    @classmethod
    def load_custom_model(cls, model_name: str) -> Optional[ChatModel]:
        """
        Dynamically load a custom model plugin from the plugins directory.
        
        Args:
            model_name (str): Name of the model file (without .py extension)
        
        Returns:
            Optional[ChatModel]: Instantiated custom model or None if not found
        """
        plugin_dir = cls.ensure_plugin_dir()
        plugin_path = os.path.join(plugin_dir, f"{model_name}.py")
        
        if not os.path.exists(plugin_path):
            return None
        
        try:
            # Dynamically import the module
            spec = importlib.util.spec_from_file_location(model_name, plugin_path)
            module = importlib.util.module_from_spec(spec)
            sys.modules[model_name] = module
            spec.loader.exec_module(module)
            
            # Find and instantiate the first ChatModel subclass
            for name, cls in module.__dict__.items():
                if (isinstance(cls, type) and 
                    issubclass(cls, ChatModel) and 
                    cls is not ChatModel):
                    return cls()
            
            raise ValueError(f"No ChatModel subclass found in {model_name}.py")
        
        except Exception as e:
            print(f"Error loading custom model {model_name}: {e}")
            return None

# Modified plugin loading function
def get_model(model_type: str, model_name: str) -> ChatModel:
    """
    Unified model loading function supporting entry point and custom plugins.
    
    Args:
        model_type (str): Type of model (e.g., 'openai', 'anthropic', 'custom')
        model_name (str): Name of the specific model
    
    Returns:
        ChatModel: Instantiated model
    
    Raises:
        ValueError: If no suitable model is found
    """
    if model_type == 'custom':
        # Try loading from custom plugins directory
        custom_model = CustomModelLoader.load_custom_model(model_name)
        if custom_model:
            return custom_model
        raise ValueError(f"Custom model {model_name} not found")
    
    # Fallback to entry point loading for other model types
    try:
        from importlib.metadata import entry_points
        
        eps = entry_points().select(group='gourami.model_plugins')
        for ep in eps:
            if f"{model_type}.{model_name}" == ep.name:
                ModelClass = ep.load()
                return ModelClass()
        
        raise ValueError(f"No model plugin found for {model_type}.{model_name}")
    
    except Exception as e:
        raise ValueError(f"Error loading model plugin: {e}")