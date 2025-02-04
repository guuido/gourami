import uvicorn
from gourami.core.config import get_settings

def run_server():
    settings = get_settings()
    uvicorn.run("gourami.api.main:app", host=settings.HOST, port=settings.PORT, reload=False)