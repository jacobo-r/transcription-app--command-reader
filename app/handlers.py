import asyncio
import time
import os
from pathlib import Path
from .bus import Bus, Command

class Handlers:
    def __init__(self, bus: Bus, pdf_dir: Path, pdf_wait_window_s: int, user_id_ref=None):
        self.bus = bus
        self.pdf_dir = pdf_dir
        self.wait_s = pdf_wait_window_s
        self.user_id_ref = user_id_ref  # Reference to user_id from HTTPAPI
        
        # Audio state (minimal, server is source of truth)
        self.audio_state = {
            'is_playing': False,
            'current_file': 'audio.mp3',
            'position': 0,
            'duration': 180
        }

    def _add_user_id(self, payload):
        """Add user_id to payload if available"""
        if self.user_id_ref and hasattr(self.user_id_ref, 'user_id') and self.user_id_ref.user_id:
            payload['user_id'] = self.user_id_ref.user_id
        return payload

    async def run(self, stop_event: asyncio.Event):
        while not stop_event.is_set():
            try:
                cmd = await asyncio.wait_for(self.bus.commands.get(), timeout=1.0)
                await self._handle_command(cmd, stop_event)
                self.bus.commands.task_done()
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                print(f"❌ Error handling command: {e}")

    async def _handle_command(self, cmd: Command, stop_event: asyncio.Event):
        """Handle incoming commands"""
        print(f"🎯 COMMAND: {cmd.type}")
        
        if cmd.type == "stop":
            # Set the stop event to trigger application shutdown
            stop_event.set()
        elif cmd.type == "check_pdf_folder":
            await self._check_pdf_window()
        elif cmd.type == "pdf_detected":
            await self._send_pdf(cmd.payload)
        elif cmd.type == "play_pause":
            await self._play_pause()
        elif cmd.type == "backward_audio":
            await self._backward_audio()
        elif cmd.type == "forward_audio":
            await self._forward_audio()
        elif cmd.type == "previous_audio":
            await self._previous_audio()
        elif cmd.type == "next_audio":
            await self._next_audio()
        elif cmd.type == "copy_transcription":
            await self._copy_transcription()
        elif cmd.type == "save_edited_transcription":
            await self._save_edited_transcription()

    async def _check_pdf_window(self):
        """Wait a short window for a file to appear; if none, still exit quickly."""
        print("⏳ Waiting 5 seconds for PDF creation...")
        deadline = asyncio.get_event_loop().time() + self.wait_s
        while asyncio.get_event_loop().time() < deadline:
            found = list(self.pdf_dir.glob("*.pdf"))
            if found:
                first_pdf = found[0]
                await self._send_pdf(first_pdf)
                print(f"✅ PDF folder check completed - sent 1 file: {first_pdf.name}")
                return
            await asyncio.sleep(0.25)
        print("✅ PDF folder check completed - no files found")

        # Estas líneas fueron agregadas para subir el ctrl+9
        await self.bus.outbound.put({
            "command": "check_pdf_folder",
            "result": "no_files_found",
            "timestamp": time.time(),
            "user_id": self.user_id_ref
        })
        ###

    async def _send_pdf(self, path: Path):
        """Send PDF file via WebSocket"""
        if not path.exists():
            return
            
        try:
            # Read PDF file
            with open(path, 'rb') as f:
                pdf_data = f.read()
            
            # Send via WebSocket
            payload = {
                'command': 'submit_pdf',
                'pdf_data': pdf_data.hex(),  # Convert to hex string for JSON
                'pdf_filename': path.name,
                'timestamp': time.time()
            }
            await self.bus.outbound.put(self._add_user_id(payload))

            # Delete the PDF file after successful send
            os.remove(path)
            print(f"📄 PDF sent and deleted: {path.name}")
            
        except Exception as e:
            print(f"❌ Error processing PDF {path}: {e}")

    async def _play_pause(self):
        """Toggle play/pause"""
        self.audio_state['is_playing'] = not self.audio_state['is_playing']
        payload = {
            'command': 'play_pause',
            'state': self.audio_state,
            'timestamp': time.time()
        }
        await self.bus.outbound.put(self._add_user_id(payload))

    async def _backward_audio(self):
        """Skip backward 10 seconds"""
        self.audio_state['position'] = max(
            self.audio_state['position'] - 10,
            0
        )
        payload = {
            'command': 'backward_audio',
            'state': self.audio_state,
            'timestamp': time.time()
        }
        await self.bus.outbound.put(self._add_user_id(payload))

    async def _forward_audio(self):
        """Skip forward 10 seconds"""
        self.audio_state['position'] = min(
            self.audio_state['position'] + 10,
            self.audio_state['duration']
        )
        payload = {
            'command': 'forward_audio',
            'state': self.audio_state,
            'timestamp': time.time()
        }
        await self.bus.outbound.put(self._add_user_id(payload))

    async def _previous_audio(self):
        """Previous audio file"""
        self.audio_state['current_file'] = f'audio_{int(time.time())-1}.mp3'
        self.audio_state['position'] = 0
        payload = {
            'command': 'previous_audio',
            'state': self.audio_state,
            'timestamp': time.time()
        }
        await self.bus.outbound.put(self._add_user_id(payload))

    async def _next_audio(self):
        """Next audio file"""
        self.audio_state['current_file'] = f'audio_{int(time.time())}.mp3'
        self.audio_state['position'] = 0
        payload = {
            'command': 'next_audio',
            'state': self.audio_state,
            'timestamp': time.time()
        }
        await self.bus.outbound.put(self._add_user_id(payload))

    async def _copy_transcription(self):
        """Request transcription from server"""
        payload = {
            'command': 'get_transcription',
            'timestamp': time.time()
        }
        await self.bus.outbound.put(self._add_user_id(payload))

    async def _save_edited_transcription(self):
        """Save edited transcription from clipboard"""
        try:
            import pyperclip
            clipboard_content = pyperclip.paste()
            print("Copied content =>", clipboard_content)
            payload = {
                'command': 'save_edited_transcription',
                'edited_transcription_content': clipboard_content
            }
            await self.bus.outbound.put(self._add_user_id(payload))
        except Exception as e:
            print(f"❌ Error saving edited transcription: {e}")

