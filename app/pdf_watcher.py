import asyncio
from pathlib import Path
from watchfiles import awatch
from .bus import Bus, Command

class PDFWatcher:
    def __init__(self, bus: Bus, folder: Path, pattern: str):
        self.bus = bus
        self.folder = folder
        self.pattern = pattern

    async def start(self):
        self.folder.mkdir(parents=True, exist_ok=True)
        print(f"📁 PDF monitoring started: {self.folder}")
        
        try:
            async for changes in awatch(self.folder):
                # changes = set of (Change.added|modified|deleted, path)
                for change_type, path_str in changes:
                    path = Path(path_str)
                    if path.match(self.pattern) and change_type.name == 'added':
                        print(f"📄 New PDF detected: {path.name}")
                        await self.bus.commands.put(Command("pdf_detected", path))
        except Exception as e:
            print(f"❌ Error in PDF watcher: {e}")



