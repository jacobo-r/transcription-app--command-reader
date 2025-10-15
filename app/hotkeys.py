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
            '1': 'play_pause',
            '2': 'backward_audio',
            '3': 'forward_audio',
            '4': 'previous_audio',
            '5': 'next_audio',
            '6': 'copy_transcription',
            '7': 'save_edited_transcription',
            '9': 'check_pdf_folder'
        }

    async def start(self):
        self._loop = asyncio.get_running_loop()
        self._listener = keyboard.Listener(on_press=self._on_press, on_release=self._on_release)
        self._listener.start()
        print("🎮 Hotkey listener started")
        print("Hotkeys: Ctrl+1(Play/Pause) Ctrl+2(Backward) Ctrl+3(Forward)")
        print("         Ctrl+4(Previous) Ctrl+5(Next) Ctrl+6(Transcription)")
        print("         Ctrl+7(Save Edited) Ctrl+9(Check PDF Folder)")
        print("Press ESC to exit\n")
        
        # Keep task alive
        while True:
            await asyncio.sleep(3600)

    def _on_press(self, key):
        """Handle key press events (like v1)"""
        try:
            # Add key to pressed set
            self.pressed_keys.add(key)
            
            # Check if Ctrl is pressed and we have a number key
            if Key.ctrl in self.pressed_keys:
                # Look for number keys (1-9)
                for pressed_key in self.pressed_keys:
                    if hasattr(pressed_key, 'char') and pressed_key.char in self.key_mappings:
                        command = self.key_mappings[pressed_key.char]
                        self._loop.call_soon_threadsafe(
                            self.bus.commands.put_nowait, Command(command)
                        )
                        break
                    elif hasattr(pressed_key, 'vk') and pressed_key.vk in range(18, 25):  # vk 18-24 are 1-6
                        # Map vk codes to actual numbers (cross-platform compatibility)
                        vk_to_char = {18: '1', 19: '2', 20: '3', 21: '4', 22: '6', 23: '5'}
                        char = vk_to_char.get(pressed_key.vk)
                        if char and char in self.key_mappings:
                            command = self.key_mappings[char]
                            self._loop.call_soon_threadsafe(
                                self.bus.commands.put_nowait, Command(command)
                            )
                            break
                    elif hasattr(pressed_key, 'vk') and pressed_key.vk in range(25, 28):  # vk 25-27 are 7-9
                        # Map vk codes for 7-9
                        vk_to_char = {25: '7', 26: '8', 27: '9'}
                        char = vk_to_char.get(pressed_key.vk)
                        if char and char in self.key_mappings:
                            command = self.key_mappings[char]
                            self._loop.call_soon_threadsafe(
                                self.bus.commands.put_nowait, Command(command)
                            )
                            break
        
        except Exception as e:
            print(f"❌ Error in on_key_press: {e}")

    def _on_release(self, key):
        """Handle key release events"""
        try:
            # Remove key from pressed set
            self.pressed_keys.discard(key)
            
            # Handle ESC key
            if hasattr(key, 'name') and key.name.lower() == 'esc':
                self._loop.call_soon_threadsafe(
                    self.bus.commands.put_nowait, Command("stop")
                )
                return False  # Stop the listener
                
        except Exception as e:
            print(f"❌ Error in on_key_release: {e}")

    async def stop(self):
        if self._listener:
            self._listener.stop()


