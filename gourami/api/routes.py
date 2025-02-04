from logging import getLogger
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from gourami.core.model import ChatModel
from gourami.core.config import get_settings, ExecutionStrategy
from gourami.plugins import get_model
from gourami.plugins.custom_plugin import CustomModelLoader
from concurrent.futures import ProcessPoolExecutor,ThreadPoolExecutor
import asyncio

router = APIRouter()
settings = get_settings()

# Create executor according to chosen execution strategy 
if settings.EXECUTION_STRATEGY == ExecutionStrategy.THREAD_POOL:
    executor = ThreadPoolExecutor(max_workers=settings.POOL_SIZE)
elif settings.EXECUTION_STRATEGY == ExecutionStrategy.PROCESS_POOL:
    executor = ProcessPoolExecutor(max_workers=settings.POOL_SIZE)
else:
    raise ValueError(f"Unsupported execution strategy: {settings.EXECUTION_STRATEGY}")

try:
    model = get_model(model_type=settings.MODEL_TYPE)
except Exception as e:
    logger = getLogger("app")
    logger.error(f"Error loading model: {e}")
    loop = asyncio.get_event_loop()
    loop.stop()


@router.websocket("/chat")
async def chat(websocket: WebSocket):
    """
    Handle WebSocket communication for real-time chatbot interaction.
    """
    logger = getLogger("app")

    await websocket.accept()
    logger.info(f"New WebSocket connection: {websocket.client}")

    try:
        while True:
            # Receive a message from the user
            message = await websocket.receive_text()

            logger.info(f"Received message from {websocket.client}")

            # Send the message to the model and get a response

            model_response = await asyncio.get_event_loop().run_in_executor(
                executor, model.predict, message
            )

            # Send the model response back to the user
            await websocket.send_text(model_response)
            logger.info(f"Response sent to {websocket.client}") 

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: {websocket.client}")
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        await websocket.close(code=1000)  # Close connection gracefully

@router.get("/health")
async def health_check():
    return {"status": "healthy", "model_loaded": model is not None}