import asyncio
import keyboard
from .bus import Bus, Command

class HotkeyAdapter:
    def __init__(self, bus: Bus, hotkey_stop: str = "", hotkey_check_pdf: str = ""):
        self.bus = bus
        self._loop = None
        self._running = True

        # Map de teclas → comandos
        self.key_mappings = {
            # F keys disponibles
            'f2': 'play_pause',
            'f3': 'backward_audio',
            'f5': 'forward_audio',
            'f7': 'previous_audio',
            'f11': 'next_audio',
            'f12': 'keep_audio', # agregado

            'ctrl+1': 'copy_transcription',
            'ctrl+3': 'save_edited_transcription',
            'ctrl+5': 'check_pdf_folder',
        }

    async def start(self):
        """Inicia el listener global de hotkeys."""
        self._loop = asyncio.get_running_loop()

        print("🎮 Hotkey listener started (keyboard lib)")
        print("Atajos activos:")
        for combo, cmd in self.key_mappings.items():
            print(f"  {combo:<12} → {cmd}")

        # Registrar los hotkeys globales
        for combo, cmd in self.key_mappings.items():
            keyboard.add_hotkey(combo, self._trigger_command, args=(cmd,))

        # Mantener tarea viva mientras la app corre
        try:
            while self._running:
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            pass
        finally:
            self.stop()
            print("⭕️ Hotkey listener stopped")

    def _trigger_command(self, cmd: str):
        """Envía el comando al bus desde el hook global."""
        if self._loop and self.bus:
            self._loop.call_soon_threadsafe(self.bus.commands.put_nowait, Command(cmd))
            print(f"🟢 Command triggered: {cmd}")

    def stop(self):
        """Detiene todos los hotkeys registrados."""
        keyboard.unhook_all_hotkeys()
        self._running = False