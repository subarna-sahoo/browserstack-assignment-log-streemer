from fastapi import FastAPI
from event_bus import EventBus
from last_n import BlockScanLastN
from tailer import NewlineFramedTailer
from api.routers import mount_routes
import os
import sys



def create_app(log_file: str) -> FastAPI:
    bus = EventBus()
    lastn = BlockScanLastN(encoding="utf-8")

    tailer = NewlineFramedTailer(log_file, bus, poll_interval=0.2, encoding="utf-8")
    tailer.start()

    app = FastAPI(title="Live Log Tail")

    # Dependency injection into routes
    app.include_router(mount_routes(bus, lastn, log_file))

    return app

LOG_FILE = "app.log"

app = create_app(LOG_FILE)