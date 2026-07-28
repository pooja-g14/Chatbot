from fastapi import FastAPI
from main import run_agent
from fastapi.responses import StreamingResponse, HTMLResponse
from dotenv import load_dotenv
from pydantic import BaseModel
load_dotenv()
import uvicorn

import logging

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

app = FastAPI()

class AgentRequest(BaseModel):
    message: str

@app.post("/run_agent")
async def run(request: AgentRequest):
    logger.info(f"SERVER: /run_agent received with message: {request.message}")
    def generate():
        # This calls the generator in main.py
        for sentence in run_agent(request.message):
            # Format as plain text or Server-Sent Events
            logger.info(f"SENTENCE STREAMED: {sentence}")
            yield sentence
            
    return StreamingResponse(generate(), media_type="text/plain")

@app.get("/", response_class=HTMLResponse)
async def index():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
