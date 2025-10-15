#!/usr/bin/env python3
"""
Debug script to test hotkey detection on any PC.
Run this to see exactly what key codes are being detected.
"""

from pynput import keyboard
from pynput.keyboard import Key

def _vk_to_digit(vk):
    """Same mapping as in the main app"""
    vk_to_char = {
        49: '1', 50: '2', 51: '3', 52: '4', 53: '5', 54: '6', 55: '7', 56: '8', 57: '9',
        97: '1', 98: '2', 99: '3', 100: '4', 101: '5', 102: '6', 103: '7', 104: '8', 105: '9',
        18: '1', 19: '2', 20: '3', 21: '4', 22: '5', 23: '6'
    }
    return vk_to_char.get(vk)

def on_press(key):
    """Debug key press detection"""
    print(f"🔍 Key pressed: {key}")
    print(f"   Type: {type(key)}")
    print(f"   Has vk: {hasattr(key, 'vk')}")
    if hasattr(key, 'vk'):
        print(f"   vk code: {key.vk}")
        digit = _vk_to_digit(key.vk)
        print(f"   Mapped to: {digit}")
    print(f"   Has char: {hasattr(key, 'char')}")
    if hasattr(key, 'char'):
        print(f"   char: {repr(key.char)}")
    print(f"   Has modifiers: {hasattr(key, 'modifiers')}")
    if hasattr(key, 'modifiers'):
        print(f"   modifiers: {key.modifiers}")
    print("-" * 40)

def on_release(key):
    """Debug key release detection"""
    if hasattr(key, 'name') and key.name.lower() == 'esc':
        print("🛑 ESC pressed - exiting debug")
        return False

if __name__ == "__main__":
    print("🔍 Hotkey Debug Script")
    print("Press Ctrl+1, Ctrl+2, etc. to see what key codes are detected")
    print("Press ESC to exit")
    print("=" * 50)
    
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()
