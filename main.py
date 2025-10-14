#!/usr/bin/env python3
"""
Audio Transcription Controller v2
Clean async-first architecture
"""
import asyncio
from app.lifecycle import run_app
from app.config import load_config

def main():
    """Main entry point"""
    try:
        cfg = load_config()
        asyncio.run(run_app(cfg))
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except Exception as e:
        print(f"❌ Fatal error: {e}")

if __name__ == "__main__":
    main()

