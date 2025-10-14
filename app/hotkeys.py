from pynput import keyboard
import asyncio
from .bus import Bus, Command

class HotkeyAdapter:
    def __init__(self, bus: Bus, hotkey_stop: str, hotkey_check_pdf: str):
        self.bus = bus
        self.hotkey_stop = hotkey_stop.lower()
        self.hotkey_check_pdf = hotkey_check_pdf.lower()
        self._listener = None
        self._loop = None
        
        # Map hotkey names to commands (extending original functionality)
        self.hotkey_mappings = {
            'f1': 'stop',
            'f2': 'check_pdf_folder',
            'ctrl+1': 'play_pause',
            'ctrl+2': 'backward_audio',
            'ctrl+3': 'forward_audio',
            'ctrl+4': 'previous_audio',
            'ctrl+5': 'next_audio',
            'ctrl+6': 'copy_transcription',
            'ctrl+7': 'save_edited_transcription',
            'ctrl+9': 'check_pdf_folder',
        }

    async def start(self):
        self._loop = asyncio.get_running_loop()
        self._listener = keyboard.Listener(on_release=self._on_release)
        self._listener.start()
        print("🎮 Hotkey listener started")
        print("Hotkeys: Ctrl+1(Play/Pause) Ctrl+2(Backward) Ctrl+3(Forward)")
        print("         Ctrl+4(Previous) Ctrl+5(Next) Ctrl+6(Transcription)")
        print("         Ctrl+7(Save Edited) Ctrl+9(Check PDF Folder)")
        print("         F1(Stop) F2(Check PDF Folder)")
        print("Press ESC to exit\n")
        
        # Keep task alive
        while True:
            await asyncio.sleep(3600)

    def _on_release(self, key):
        try:
            # Handle special keys
            if hasattr(key, 'name'):
                key_name = key.name.lower()
            else:
                key_name = str(key).lower()
            
            # Check for Ctrl combinations
            if hasattr(key, 'char') and key.char and key.char.isdigit():
                # This is a number key, check if Ctrl is pressed
                ctrl_combo = f"ctrl+{key.char}"
                if ctrl_combo in self.hotkey_mappings:
                    command = self.hotkey_mappings[ctrl_combo]
                    self._loop.call_soon_threadsafe(
                        self.bus.commands.put_nowait, Command(command)
                    )
                    return
            
            # Check direct key mappings
            if key_name in self.hotkey_mappings:
                command = self.hotkey_mappings[key_name]
                self._loop.call_soon_threadsafe(
                    self.bus.commands.put_nowait, Command(command)
                )
                return
            
            # Handle ESC key
            if key_name == 'esc':
                self._loop.call_soon_threadsafe(
                    self.bus.commands.put_nowait, Command("stop")
                )
                return False  # Stop the listener
                
        except Exception as e:
            print(f"❌ Error in hotkey handler: {e}")

    async def stop(self):
        if self._listener:
            self._listener.stop()

