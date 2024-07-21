from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
import subprocess
import logging
from starlette.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
import json
import asyncio
import traceback

load_dotenv()
masil_server_url = os.getenv('masil_server_url')

origins = [
   "*"
]

app = FastAPI(
    openapi_url="/api/openapi.json",
    docs_url="/api/docs",
    redoc_url=None  # Disable ReDoc
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Hello World"}


@app.get("/api/home")
def home():
    return {"messange": "home"}


@app.get("/api/crawling/government")
async def do_government():
    try:
        result = await asyncio.to_thread(subprocess.run, ["python3", "src/slack_government.py"], stderr=subprocess.PIPE)
        return {"message": "Government24 crawling executed successfully."} if result.returncode == 0 else {"error": result.stderr.decode('utf-8', errors = 'ignore')}
    except asyncio.TimeoutError:
        return {"error": "Timeout exceeded"}
    except Exception as e:
        error_traceback = traceback.format_exc()
        return {"error": repr(e), "traceback": error_traceback}


@app.get("/api/crawling/local{i}")
async def do_local(i: int, request: Request):
    try:
        result = await asyncio.to_thread(subprocess.run, ["python3", f"src/slack_local{i}.py"], stderr=subprocess.PIPE)
        return {"message": "Local crawling executed successfully."} if result.returncode == 0 else {"error": result.stderr.decode('utf-8', errors = 'ignore')}
    except asyncio.TimeoutError:
        return {"error": "Timeout exceeded"}
    except Exception as e:
        error_traceback = traceback.format_exc()
        return {"error": repr(e), "traceback": error_traceback}


@app.get("/api/test")
def do_test():
    try:
        result = subprocess.run(["python3", "src/slack_dev.py"], stderr=subprocess.PIPE)
        if result.returncode == 0:
            return {"message": "Dev crawling executed successfully."}
        else:
            return {"error": result.stderr.decode('utf-8')}
    except Exception as e:
        return {"error": str(e)}


#if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)  