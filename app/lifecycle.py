import asyncio
import signal
import contextlib
from .bus import Bus
from .ws_client import WSClient
from .pdf_watcher import PDFWatcher
from .hotkeys import HotkeyAdapter
from .http_api import HTTPAPI
from .handlers import Handlers
from .config import Config

async def run_app(cfg: Config):
    """Main application lifecycle"""
    bus = Bus()
    stop_event = asyncio.Event()

    # Initialize components
    ws = WSClient(bus, cfg.ws_url, cfg.reconnect_base_s, cfg.reconnect_max_s)
    pdf = PDFWatcher(bus, cfg.pdf_dir, cfg.pdf_glob)
    hk = HotkeyAdapter(bus, cfg.hotkey_stop, cfg.hotkey_check_pdf)
    api = HTTPAPI(bus, cfg.http_host, cfg.http_port)
    handlers = Handlers(bus, cfg.pdf_dir, cfg.pdf_wait_window_s)

    # Create tasks
    tasks = [
        asyncio.create_task(ws.start(), name="ws"),
        asyncio.create_task(pdf.start(), name="pdf"),
        asyncio.create_task(hk.start(), name="hotkeys"),
        asyncio.create_task(api.start(), name="http"),
        asyncio.create_task(handlers.run(stop_event), name="handlers"),
    ]

    # Setup signal handlers for graceful shutdown
    for sig in (signal.SIGINT, signal.SIGTERM):
        with contextlib.suppress(NotImplementedError):
            asyncio.get_running_loop().add_signal_handler(
                sig, stop_event.set
            )

    print("🎮 Audio Transcription Controller v2")
    print("✅ All components started successfully")
    
    # Wait for stop signal
    await stop_event.wait()
    print("\n👋 Shutting down application...")

    # Graceful teardown
    await ws.stop()
    await api.stop()
    
    # Cancel all tasks
    for t in tasks:
        t.cancel()
    
    # Wait for tasks to complete cancellation
    for t in tasks:
        with contextlib.suppress(asyncio.CancelledError):
            await t
    
    print("✅ Application stopped cleanly")

