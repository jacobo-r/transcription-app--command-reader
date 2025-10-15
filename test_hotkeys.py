#!/usr/bin/env python3
"""
Test script to emulate hotkey presses for the audio transcription controller.
This script simulates the exact key press sequences that were causing issues.
"""

import time
import subprocess
import sys
from pynput import keyboard
from pynput.keyboard import Key

def test_hotkeys():
    """Test the hotkey functionality by emulating key presses"""
    print("🧪 Starting hotkey test...")
    print("This will simulate Ctrl+1, Ctrl+2, Ctrl+3 key presses")
    print("Make sure the audio transcription controller is running!")
    print()
    
    # Wait a moment for user to see the message
    time.sleep(2)
    
    # Create a keyboard controller
    controller = keyboard.Controller()
    
    try:
        # Test sequence 1: Ctrl+1 (should trigger play_pause)
        print("Testing Ctrl+1 (play_pause)...")
        controller.press(Key.ctrl_l)
        time.sleep(0.1)
        controller.press('1')
        time.sleep(0.1)
        controller.release('1')
        controller.release(Key.ctrl_l)
        time.sleep(1)
        
        # Test sequence 2: Ctrl+2 (should trigger backward_audio)
        print("Testing Ctrl+2 (backward_audio)...")
        controller.press(Key.ctrl_l)
        time.sleep(0.1)
        controller.press('2')
        time.sleep(0.1)
        controller.release('2')
        controller.release(Key.ctrl_l)
        time.sleep(1)
        
        # Test sequence 3: Ctrl+3 (should trigger forward_audio)
        print("Testing Ctrl+3 (forward_audio)...")
        controller.press(Key.ctrl_l)
        time.sleep(0.1)
        controller.press('3')
        time.sleep(0.1)
        controller.release('3')
        controller.release(Key.ctrl_l)
        time.sleep(1)
        
        # Test sequence 4: Ctrl+4 (should trigger previous_audio)
        print("Testing Ctrl+4 (previous_audio)...")
        controller.press(Key.ctrl_l)
        time.sleep(0.1)
        controller.press('4')
        time.sleep(0.1)
        controller.release('4')
        controller.release(Key.ctrl_l)
        time.sleep(1)
        
        # Test sequence 5: Ctrl+5 (should trigger next_audio)
        print("Testing Ctrl+5 (next_audio)...")
        controller.press(Key.ctrl_l)
        time.sleep(0.1)
        controller.press('5')
        time.sleep(0.1)
        controller.release('5')
        controller.release(Key.ctrl_l)
        time.sleep(1)
        
        # Test sequence 6: Ctrl+6 (should trigger copy_transcription)
        print("Testing Ctrl+6 (copy_transcription)...")
        controller.press(Key.ctrl_l)
        time.sleep(0.1)
        controller.press('6')
        time.sleep(0.1)
        controller.release('6')
        controller.release(Key.ctrl_l)
        time.sleep(1)
        
        # Test sequence 7: Ctrl+7 (should trigger save_edited_transcription)
        print("Testing Ctrl+7 (save_edited_transcription)...")
        controller.press(Key.ctrl_l)
        time.sleep(0.1)
        controller.press('7')
        time.sleep(0.1)
        controller.release('7')
        controller.release(Key.ctrl_l)
        time.sleep(1)
        
        # Test sequence 8: Ctrl+9 (should trigger check_pdf_folder)
        print("Testing Ctrl+9 (check_pdf_folder)...")
        controller.press(Key.ctrl_l)
        time.sleep(0.1)
        controller.press('9')
        time.sleep(0.1)
        controller.release('9')
        controller.release(Key.ctrl_l)
        time.sleep(1)
        
        print("✅ All hotkey tests completed!")
        print("Check the audio transcription controller output to see if commands were received.")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False
    
    return True

def test_virtual_key_codes():
    """Test using virtual key codes directly (like the debug output showed)"""
    print("\n🔬 Testing virtual key code simulation...")
    print("This simulates the exact key codes from your debug output")
    
    controller = keyboard.Controller()
    
    try:
        # Simulate the exact sequence from debug output
        # {<Key.ctrl_l: <162>>}
        # {<Key.ctrl_l: <162>>, <49>}
        print("Simulating Ctrl+1 with virtual key codes...")
        
        # Press Ctrl
        controller.press(Key.ctrl_l)
        time.sleep(0.1)
        
        # Press '1' (which should generate vk 49)
        controller.press('1')
        time.sleep(0.1)
        
        # Release '1'
        controller.release('1')
        time.sleep(0.1)
        
        # Release Ctrl
        controller.release(Key.ctrl_l)
        time.sleep(1)
        
        print("✅ Virtual key code test completed!")
        
    except Exception as e:
        print(f"❌ Error during virtual key code testing: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🎮 Audio Transcription Controller - Hotkey Test Script")
    print("=" * 60)
    
    # Check if pynput is available
    try:
        import pynput
    except ImportError:
        print("❌ pynput is not installed. Please install it with: pip install pynput")
        sys.exit(1)
    
    print("Make sure the audio transcription controller is running before starting the test!")
    input("Press Enter when ready to start testing...")
    
    # Run the tests
    success1 = test_hotkeys()
    success2 = test_virtual_key_codes()
    
    if success1 and success2:
        print("\n🎉 All tests completed successfully!")
        print("Check the audio transcription controller logs to verify commands were received.")
    else:
        print("\n❌ Some tests failed. Check the error messages above.")
        sys.exit(1)
