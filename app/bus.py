from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Any
import asyncio

# Commands the app understands
CommandType = Literal[
    "stop",
    "check_pdf_folder",
    "pdf_detected",     # payload: Path
    "ws_send",          # payload: dict
    "play_pause",
    "backward_audio",
    "forward_audio",
    "previous_audio",
    "next_audio",
    "copy_transcription",
    "save_edited_transcription",
]

@dataclass(frozen=True)
class Command:
    type: CommandType
    payload: Any = None

class Bus:
    def __init__(self) -> None:
        self.commands: asyncio.Queue[Command] = asyncio.Queue()
        self.outbound: asyncio.Queue[dict] = asyncio.Queue()  # to WS


