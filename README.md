# Gourami: Open Framework for Chatbots with Pluggable Models
Gourami is an open framework for building chatbots with pluggable AI models. It leverages **FastAPI** and **Uvicorn** to provide a scalable and real-time API for chatbot interactions. The framework supports multiple AI models (e.g., OpenAI, Hugging Face, Anthropic, Google, Mixtral, LLaMA) through a plugin system, allowing users to easily integrate and switch between models.

### Current Status
Gourami is in active development. The base framework is functional, but it is still a work in progress. Some features, such as automated tests, advanced configurations and plugins are still missing or need improvement. The framework is intended for experimentation and development, and while it is already usable, it may require further tuning before being ready for production environments.
Your contributions are welcome! If you're interested in helping improve the framework, fixing bugs, adding new features or working on missing components like tests and documentation, please feel free to contribute.

## Features

- **Pluggable AI Models**: Easily integrate and switch between different AI models using a plugin system.
- **Real-Time Chat**: WebSocket support for real-time chatbot interactions.
- **Flexible Configuration**: Configure models, execution strategies and server settings via a JSON file or CLI arguments.
- **Scalable Execution**: Supports thread pools and process pools for handling heavy workloads.
- **Extensible Model Support**: The framework is designed to easily integrate new AI models. In future developments, you'll be able to add custom plugins to support models not yet included.

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/guuido/gourami.git
   cd gourami
   ```

2. **Install Dependencies**:
   ```bash
   pip install .[modeltype]
   ```
   where `modeltype` is the model type you intend to use (available types: `openai`, `anthropic`, `google`, `huggingface`, `mixtral`, `llama`)

## Usage

### Starting the Server

Use the following command to start the Gourami server:

```bash
gourami start --host 0.0.0.0 --port 5000 --config-file config.json
```

#### CLI Options:
- `--host, -h`: Host address to bind the server (default: `0.0.0.0`).
- `--port, -p`: Port to run the server (default: `5000`).
- `--config-file, -f`: Path to the configuration file (optional).

### Configuration

Gourami supports configuration via a JSON file. Here’s an example configuration file (`config.json`):

```json
{
   "host": "0.0.0.0",
   "port": 5000,
   "model_type": "huggingface",
   "execution_strategy": "thread",
   "pool_size": 4,
   "model_params": {
     "model_name": "facebook/opt-350m",
     "temperature": 0.7,
     "max_tokens": 1000,
     "device": "cpu"
  }
}
```

#### Key Configuration Fields:
- `model_type`: The type of model to use (e.g., `huggingface`, `openai`, `anthropic`).
- `execution_strategy`: Execution strategy for handling requests (`thread` or `process`).
- `pool_size`: Number of workers in the thread/process pool.
- `model_params`: Model-specific parameters (e.g., `model_name`, `temperature`, `max_tokens`).

### Execution Strategies

Gourami supports two execution strategies for handling requests:

1. **Thread Pool**:
   - Suitable for I/O-bound tasks or lighter CPU-bound tasks.
   - Configured with `execution_strategy: thread`.

2. **Process Pool**:
   - Suitable for heavy CPU-bound tasks (e.g., large models on CPU).
   - Configured with `execution_strategy: process`.

### API Endpoints

#### WebSocket Chat (`/chat`)
- **Description**: Real-time chatbot interaction via WebSocket.
- **Usage**:
  ```python
  import asyncio
  import websockets

  async def chat():
      async with websockets.connect("ws://localhost:5000/chat") as websocket:
          await websocket.send("Hello, Gourami!")
          response = await websocket.recv()
          print(response)

  asyncio.get_event_loop().run_until_complete(chat())
  ```

#### Health Check (`/health`)
- **Description**: Check if the server is running and the model is loaded.
- **Response**:
  ```json
  {
     "status": "healthy",
     "model_loaded": true
  }
  ```

### Plugins

Gourami supports pluggable AI models through a plugin system. Each plugin implements the `ChatModel` interface and provides model-specific configuration.

#### Available Plugins:
- **OpenAI**: `gourami.plugins.openai_plugin:OpenAIModel`
- **Anthropic**: `gourami.plugins.anthropic_plugin:AnthropicModel`
- **Google**: `gourami.plugins.google_plugin:GoogleModel`
- **Hugging Face**: `gourami.plugins.huggingface_plugin:HuggingFaceModel`
- **Mixtral**: `gourami.plugins.mixtral_plugin:MixtralModel`
- **LLaMA**: `gourami.plugins.llama_plugin:LlamaModel`

### Contributing

Contributions are welcome! If you'd like to help develop Gourami, here are some ways you can contribute:

1.  **Fix Bugs:** Help with identifying and fixing bugs in the code.
2.  **Add Tests:** The project is still missing automated tests. Contributions to add tests for various components would be very helpful.
3.  **Improve Documentation:** Help by clarifying documentation or adding more usage examples.
4.  **Add New Features:** Implement new features such as additional configuration options or enhancements to the plugin system.
5.  **Optimize Performance:** Work on optimizing code for better scalability and performance.
6.  **Create Custom Plugins:** Contribute new models by writing custom plugins to extend the framework’s capabilities.

### License

Gourami is licensed under the MIT License. See [LICENSE](LICENSE) for details.
