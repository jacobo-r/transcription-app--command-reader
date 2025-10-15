import asyncio
import json
import contextlib
import time
import websockets
from websockets.client import WebSocketClientProtocol
from .bus import Bus

class WSClient:
    def __init__(self, bus: Bus, url: str, base: float, max_delay: float, user_id_ref=None):
        self.bus = bus
        self.url = url
        self.base = base
        self.max_delay = max_delay
        self.ws: WebSocketClientProtocol | None = None
        self._stop = asyncio.Event()
        self.user_id_ref = user_id_ref  # Reference to user_id from HTTPAPI

    async def start(self):
        sender = asyncio.create_task(self._sender())
        try:
            await self._run_reconnect_loop()
        finally:
            sender.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await sender

    async def _run_reconnect_loop(self):
        delay = self.base
        while not self._stop.is_set():
            try:
                print(f"🔌 Connecting to WebSocket: {self.url}")
                async with websockets.connect(self.url) as ws:
                    self.ws = ws
                    delay = self.base  # reset backoff on success
                    print("✅ WebSocket connected!")
                    await self._receiver(ws)
            except Exception as e:
                print(f"❌ WebSocket connection error: {e}")
                await asyncio.sleep(delay)
                delay = min(delay * 2, self.max_delay)

    async def _receiver(self, ws: WebSocketClientProtocol):
        try:
            async for msg in ws:
                await self._handle_message(msg)
        except websockets.exceptions.ConnectionClosed:
            print("🔌 WebSocket connection closed")
        except Exception as e:
            print(f"❌ Error in WebSocket receiver: {e}")

    async def _handle_message(self, message):
        """Handle incoming WebSocket message"""
        try:
            data = json.loads(message)
            print(f"📨 Received: {data}")
            
            # Handle different message types
            if data.get('type') == 'frontend_response' and data.get('command') == 'get_transcription':
                transcription = data.get('transcription', '')
                if transcription:
                    # Copy to clipboard
                    import pyperclip
                    pyperclip.copy(transcription)
                    print("📋 Transcription copied to clipboard!")
        
        except Exception as e:
            print(f"❌ Error handling message: {e}")

    async def _sender(self):
        while not self._stop.is_set():
            try:
                payload = await asyncio.wait_for(self.bus.outbound.get(), timeout=1.0)
                if self.ws is not None:
                    await self.ws.send(json.dumps(payload))
                    print(f"📤 Sent: {payload}")
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                print(f"❌ Error sending message: {e}")
            finally:
                try:
                    self.bus.outbound.task_done()
                except ValueError:
                    pass  # Queue was empty

    async def stop(self):
        self._stop.set()
        if self.ws is not None:
            with contextlib.suppress(Exception):
                await self.ws.close()

