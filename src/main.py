from dotenv import load_dotenv
load_dotenv()

import asyncio
import logging
import subprocess
from contextlib import asynccontextmanager
from typing import Generator

import uvicorn
from fastapi import FastAPI, Request, Response, status
from fastapi.responses import HTMLResponse, StreamingResponse

# Bot version
BOT_VERSION = "0.1"

from bot import bot
from utils import (
    BOT_NAME,
    LOG_PATH,
    create_initial_folders,
    get_date_time,
    initialize_logging,
    terminal_html,
)

# Initialize
create_initial_folders()
console_out = initialize_logging()
time_str = get_date_time("Asia/Ho_Chi_Minh")


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        loop = asyncio.get_event_loop()
        background_tasks = set()
        task = loop.create_task(bot())
        background_tasks.add(task)
        task.add_done_callback(background_tasks.discard)
        logging.info("App initiated")
    except Exception as e:
        logging.critical(f"Error occurred while starting up app: {e}")
        raise e
    yield
    logging.info("Application close...")


# API and app handling
app = FastAPI(lifespan=lifespan, title=BOT_NAME)


@app.get("/")
async def root() -> str:
    return f"{BOT_NAME} {BOT_VERSION} is deployed on ({time_str})"


@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check() -> str:
    return f"{BOT_NAME} {BOT_VERSION} health check"


@app.get("/log")
async def log_check() -> StreamingResponse:
    async def generate_log() -> Generator[bytes, None, None]:
        console_log = console_out.getvalue()
        yield f"{console_log}".encode("utf-8")

    return StreamingResponse(generate_log())
