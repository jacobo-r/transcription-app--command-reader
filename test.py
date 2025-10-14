#!/usr/bin/env python3
"""
Test script for Audio Transcription Controller v2
Verifies all dependencies and basic functionality
"""
import sys
import asyncio
from pathlib import Path

def test_imports():
    """Test that all required modules can be imported"""
    try:
        import websockets
        import aiohttp
        import watchfiles
        import pynput
        import pyperclip
        print("✅ All core dependencies imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        return False

def test_config():
    """Test configuration loading"""
    try:
        from app.config import load_config
        cfg = load_config()
        print(f"✅ Configuration loaded: {cfg.ws_url}")
        return True
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def test_bus():
    """Test event bus creation"""
    try:
        from app.bus import Bus, Command
        bus = Bus()
        print("✅ Event bus created successfully")
        return True
    except Exception as e:
        print(f"❌ Bus creation error: {e}")
        return False

async def test_async_components():
    """Test async component creation"""
    try:
        from app.bus import Bus
        from app.ws_client import WSClient
        from app.pdf_watcher import PDFWatcher
        from app.hotkeys import HotkeyAdapter
        from app.http_api import HTTPAPI
        from app.handlers import Handlers
        from app.config import load_config
        
        cfg = load_config()
        bus = Bus()
        
        # Create components (don't start them)
        ws = WSClient(bus, cfg.ws_url, cfg.reconnect_base_s, cfg.reconnect_max_s)
        pdf = PDFWatcher(bus, cfg.pdf_dir, cfg.pdf_glob)
        hk = HotkeyAdapter(bus, cfg.hotkey_stop, cfg.hotkey_check_pdf)
        api = HTTPAPI(bus, cfg.http_host, cfg.http_port)
        handlers = Handlers(bus, cfg.pdf_dir, cfg.pdf_wait_window_s)
        
        print("✅ All async components created successfully")
        return True
    except Exception as e:
        print(f"❌ Component creation error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Audio Transcription Controller v2...")
    print()
    
    tests = [
        ("Dependencies", test_imports),
        ("Configuration", test_config),
        ("Event Bus", test_bus),
        ("Async Components", lambda: asyncio.run(test_async_components())),
    ]
    
    passed = 0
    total = len(tests)
    
    for name, test_func in tests:
        print(f"Testing {name}...")
        if test_func():
            passed += 1
        print()
    
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The application is ready to run.")
        print("Run: python main.py")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()

