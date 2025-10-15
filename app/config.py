from dataclasses import dataclass
from pathlib import Path
import os

# Handle TOML parsing for different Python versions
try:
    import tomllib  # Python 3.11+
except ImportError:
    import tomli as tomllib  # Python < 3.11

@dataclass(frozen=True)
class Config:
    ws_url: str
    pdf_dir: Path
    http_host: str = "127.0.0.1"
    http_port: int = 8080
    hotkey_stop: str = "f1"
    hotkey_check_pdf: str = "f2"
    pdf_glob: str = "*.pdf"
    pdf_wait_window_s: int = 5
    reconnect_base_s: float = 0.5
    reconnect_max_s: float = 15.0

def load_config() -> Config:
    path = Path(__file__).resolve().parent.parent / "app.toml"
    data = {}
    if path.exists():
        with path.open("rb") as f:
            data = tomllib.load(f)
    return Config(
        ws_url = os.getenv("WS_URL", data.get("ws_url", "ws://150.1.6.144:6790")),
        pdf_dir = Path(os.getenv("PDF_DIR", data.get("pdf_dir", "./pdf_for_submission"))).resolve(),
        http_host = data.get("http_host", "127.0.0.1"),
        http_port = int(data.get("http_port", 8080)),
        hotkey_stop = data.get("hotkey_stop", "f1"),
        hotkey_check_pdf = data.get("hotkey_check_pdf", "f2"),
        pdf_glob = data.get("pdf_glob", "*.pdf"),
        pdf_wait_window_s = int(data.get("pdf_wait_window_s", 5)),
        reconnect_base_s = float(data.get("reconnect_base_s", 0.5)),
        reconnect_max_s = float(data.get("reconnect_max_s", 15.0)),
    )