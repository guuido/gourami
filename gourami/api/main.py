from fastapi import FastAPI
from gourami.utils.logging import setup_logging

# Create logger before starting the server
logger = setup_logging()
logger.info("Starting Gourami server...")

from gourami.api.routes import router

app = FastAPI()
app.include_router(router)

