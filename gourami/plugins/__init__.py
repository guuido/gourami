from gourami.core.model import ChatModel
from importlib.metadata import entry_points
from gourami.core.config import get_settings

def get_model(model_type: str) -> ChatModel:
    """
    Dynamically load a model plugin based on model type and name.
    
    Args:
        model_type (str): The type of model (e.g., 'openai')
    
    Returns:
        ChatModel: An instantiated model that implements the ChatModel interface
    
    Raises:
        ValueError: If no matching model plugin is found
    """
    settings = get_settings()

    try:
        # Select entry points for the specified group
        eps = entry_points().select(group='gourami.model_plugins')
        
        # Look for an entry point that matches the model type and name
        for ep in eps:
            if f"{model_type}" == ep.name:
                ModelClass = ep.load()
                 # Get the config class from the model
                ConfigClass = ModelClass.get_config_class()       
                # Create config instance with settings
                config = ConfigClass(**settings.model_params)
                return ModelClass(config)
        
        # If no entry point is found, raise an error
        raise ValueError(f"No model plugin found for {model_type}")
    
    except Exception as e:
        raise ValueError(f"Error loading model plugin: {e}")