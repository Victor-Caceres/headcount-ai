from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from agent import run_agent

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str


@app.get("/ping")
def ping():
    return {"status": "ok"}


@app.post("/chat")
def chat(req: ChatRequest):
    try:
        result = run_agent(req.message)
        return result
    except Exception:
        return JSONResponse(
            status_code=500,
            content={"answer": "Something went wrong. Please try again.", "tools_called": []},
        )
