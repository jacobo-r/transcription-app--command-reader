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

    def _vk_to_digit(self, vk):
        """Convert virtual key code to digit character for cross-platform compatibility"""
        vk_to_char = {
            49: '1', 50: '2', 51: '3', 52: '4', 53: '5', 54: '6', 55: '7', 56: '8', 57: '9',
            97: '1', 98: '2', 99: '3', 100: '4', 101: '5', 102: '6', 103: '7', 104: '8', 105: '9',
            18: '1', 19: '2', 20: '3', 21: '4', 22: '5', 23: '6'
        }
        return vk_to_char.get(vk)

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
                    elif hasattr(pressed_key, 'vk'):
                        # Use the comprehensive vk to digit mapping for cross-platform compatibility
                        char = self._vk_to_digit(pressed_key.vk)
                        if char and char in self.key_mappings:
                            command = self.key_mappings[char]
                            self._loop.call_soon_threadsafe(
                                self.bus.commands.put_nowait, Command(command)
                            )
                            break
            
            # Fallback: Check if the current key is a Ctrl+number combination that comes as single vk
            # This handles cases where some keyboards/systems send Ctrl+1 as just vk 49
            if hasattr(key, 'vk'):
                char = self._vk_to_digit(key.vk)
                if char and char in self.key_mappings:
                    # Check if Ctrl is currently pressed (either as separate key or modifier)
                    ctrl_pressed = (Key.ctrl in self.pressed_keys or 
                                  (hasattr(key, 'modifiers') and Key.ctrl in key.modifiers))
                    if ctrl_pressed:
                        command = self.key_mappings[char]
                        self._loop.call_soon_threadsafe(
                            self.bus.commands.put_nowait, Command(command)
                        )
        
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


