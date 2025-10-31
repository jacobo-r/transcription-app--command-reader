from pynput import keyboard
from pynput.keyboard import Key
import asyncio
from .bus import Bus, Command

class HotkeyAdapter:
    def __init__(self, bus: Bus, hotkey_stop: str, hotkey_check_pdf: str):
        self.bus = bus
        self.hotkey_stop = hotkey_stop.lower()
        self.hotkey_check_pdf = hotkey_check_pdf.lower()
        self._listener = None
        self._loop = None
        self.pressed_keys = set()

        # Map number keys to commands (like v1)
        self.key_mappings = {
            Key.f1: 'play_pause',
            Key.f2: 'backward_audio',
            Key.f3: 'forward_audio',
            Key.f4: 'previous_audio',
            Key.f5: 'next_audio',
            Key.f6: 'copy_transcription',
            Key.f7: 'save_edited_transcription',
            Key.f9: 'check_pdf_folder',
            Key.f10: 'keep_audio', #agregado
            'm': 'keep_audio' #agregado
        }

    async def start(self):
        self._loop = asyncio.get_running_loop()
        self._listener = keyboard.Listener(on_press=self._on_press, on_release=self._on_release)
        self._listener.start()
        print("🎮 Hotkey listener started")
        print("Hotkeys: Ctrl+1(Play/Pause) Ctrl+2(Backward) Ctrl+3(Forward)")
        print("         Ctrl+4(Previous) Ctrl+5(Next) Ctrl+6(Transcription)")
        print("         Ctrl+7(Save Edited) Ctrl+9(Check PDF Folder)")
        print("Use Ctrl+C to exit\n")
        
        # Keep task alive
        while True:
            await asyncio.sleep(3600)

    def _on_press(self, key):
        """Handle key press events (like v1)"""
        try:
            if key in self.key_mappings:
                cmd = self.key_mappings[key]
                #Send commands to the bus
                self._loop.call_soon_threadsafe(self.bus.commands.put_nowait, Command(cmd))    
        except Exception as e:
            print(f"❌ Error in on_key_press: {e}")

    def _on_release(self, key):
        """Handle key release events"""
        pass

    async def stop(self):
        if self._listener:
            self._listener.stop()
            print("⭕️ Hotkey Listener Stopped")
