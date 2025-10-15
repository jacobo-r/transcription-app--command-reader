# Audio Transcription Controller v2 - Technical Specification

## Document Information
- **Document Type**: Technical Specification
- **Version**: 2.0.0
- **Date**: December 2024
- **Status**: Final
- **Classification**: Internal Technical Documentation

---

## 1. System Architecture

### 1.1 High-Level Architecture

The Audio Transcription Controller v2 follows a microservices-inspired architecture within a single process, using an event-driven design pattern with the following key principles:

- **Single Responsibility**: Each component handles one specific concern
- **Loose Coupling**: Components communicate only through well-defined interfaces
- **High Cohesion**: Related functionality is grouped together
- **Event-Driven**: Asynchronous message passing between components

### 1.2 Component Interaction Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    Application Lifecycle                        │
│                        (lifecycle.py)                          │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ • Signal Handling (SIGINT, SIGTERM)                     │   │
│  │ • Task Coordination                                     │   │
│  │ • Graceful Shutdown                                     │   │
│  │ • Resource Cleanup                                      │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────┬───────────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────────┐
│                      Event Bus                                   │
│                   (app/bus.py)                                   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │   Commands  │  │  Outbound   │  │   State     │              │
│  │   Queue     │  │   Queue     │  │ Management  │              │
│  │             │  │             │  │             │              │
│  │ • Hotkeys   │  │ • WebSocket │  │ • Audio     │              │
│  │ • HTTP API  │  │ • Messages  │  │ • User      │              │
│  │ • PDF Events│  │ • Responses │  │ • Session   │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
└─────────────────────┬───────────────────────────────────────────┘
                      │
    ┌─────────────────┼─────────────────┐
    │                 │                 │
┌───▼───┐         ┌───▼───┐         ┌───▼───┐
│Hotkeys│         │  PDF  │         │ HTTP  │
│Adapter│         │Watcher│         │  API  │
│       │         │       │         │       │
│ • pynput│         │ • watchfiles│         │ • aiohttp│
│ • Thread │         │ • Async     │         │ • CORS   │
│ • Bridge │         │ • Events    │         │ • REST   │
└───┬───┘         └───┬───┘         └───┬───┘
    │                 │                 │
    └─────────────────┼─────────────────┘
                      │
              ┌───────▼───────┐
              │   Handlers    │
              │ (app/handlers.py)│
              │               │
              │ • Command     │
              │   Processing  │
              │ • Business    │
              │   Logic       │
              │ • State       │
              │   Management  │
              └───────┬───────┘
                      │
              ┌───────▼───────┐
              │ WebSocket     │
              │ Client        │
              │ (app/ws_client.py)│
              │               │
              │ • Connection  │
              │ • Reconnect   │
              │ • Message     │
              │   Handling    │
              │ • Error       │
              │   Recovery    │
              └───────────────┘
```

### 1.3 Data Flow Architecture

```
Input Sources → Event Bus → Command Processing → Output Actions
     │              │              │                │
     │              │              │                │
┌────▼────┐    ┌────▼────┐    ┌────▼────┐    ┌─────▼─────┐
│ Hotkeys │    │ Commands│    │ Handlers│    │ WebSocket │
│         │    │ Queue   │    │         │    │ Client    │
│ • Ctrl+1│    │         │    │ • Audio │    │           │
│ • Ctrl+2│    │ • play_ │    │ • PDF   │    │ • Send    │
│ • F1    │    │   pause │    │ • Trans │    │ • Receive │
│ • ESC   │    │ • stop  │    │ • State │    │ • Process │
└─────────┘    └─────────┘    └─────────┘    └───────────┘
     │              │              │                │
┌────▼────┐    ┌────▼────┐    ┌────▼────┐    ┌─────▼─────┐
│ PDF     │    │ Outbound│    │ State   │    │ HTTP API  │
│ Events  │    │ Queue   │    │ Updates │    │           │
│         │    │         │    │         │    │ • Health  │
│ • File  │    │ • JSON  │    │ • Audio │    │ • User ID │
│   Added │    │ • Commands│    │ • User │    │ • Trigger │
│ • File  │    │ • Data  │    │ • Session│    │ • CORS   │
│   Process│    │ • State │    │ • Cache │    │ • REST   │
└─────────┘    └─────────┘    └─────────┘    └───────────┘
```

---

## 2. Component Specifications

### 2.1 Event Bus (`app/bus.py`)

#### Purpose
Central communication hub that decouples components and provides type-safe message passing.

#### Responsibilities
- Command routing and queuing
- Message serialization/deserialization
- Thread-safe operations
- Type validation

#### Interface
```python
class Bus:
    def __init__(self) -> None:
        self.commands: asyncio.Queue[Command] = asyncio.Queue()
        self.outbound: asyncio.Queue[dict] = asyncio.Queue()
```

#### Command Types
```python
CommandType = Literal[
    "stop",                      # Application shutdown
    "check_pdf_folder",          # Manual PDF folder check
    "pdf_detected",             # PDF file detected
    "ws_send",                  # Send WebSocket message
    "play_pause",               # Audio control
    "backward_audio",           # Audio control
    "forward_audio",            # Audio control
    "previous_audio",           # Audio control
    "next_audio",              # Audio control
    "copy_transcription",       # Transcription management
    "save_edited_transcription" # Transcription management
]
```

### 2.2 WebSocket Client (`app/ws_client.py`)

#### Purpose
Resilient WebSocket communication with automatic reconnection and error recovery.

#### Features
- **Auto-reconnect**: Exponential backoff with configurable limits
- **Message Handling**: Bidirectional message processing
- **Error Recovery**: Graceful handling of connection failures
- **Protocol Support**: JSON message format

#### Configuration
```python
class WSClient:
    def __init__(self, bus: Bus, url: str, base: float, max_delay: float):
        self.bus = bus
        self.url = url
        self.base = base          # Initial reconnect delay
        self.max_delay = max_delay # Maximum reconnect delay
```

#### Reconnection Algorithm
```python
async def _run_reconnect_loop(self):
    delay = self.base
    while not self._stop.is_set():
        try:
            async with websockets.connect(self.url) as ws:
                self.ws = ws
                delay = self.base  # Reset on success
                await self._receiver(ws)
        except Exception:
            await asyncio.sleep(delay)
            delay = min(delay * 2, self.max_delay)  # Exponential backoff
```

### 2.3 PDF Watcher (`app/pdf_watcher.py`)

#### Purpose
Real-time PDF file monitoring using async file system events.

#### Technology
- **Library**: `watchfiles` (async alternative to `watchdog`)
- **Performance**: No additional threads, event-driven
- **Pattern Matching**: Configurable file patterns
- **Event Types**: File creation, modification, deletion

#### Implementation
```python
class PDFWatcher:
    def __init__(self, bus: Bus, folder: Path, pattern: str):
        self.bus = bus
        self.folder = folder
        self.pattern = pattern

    async def start(self):
        self.folder.mkdir(parents=True, exist_ok=True)
        async for changes in awatch(self.folder):
            for change_type, path_str in changes:
                path = Path(path_str)
                if path.match(self.pattern) and change_type.name == 'added':
                    await self.bus.commands.put(Command("pdf_detected", path))
```

### 2.4 Hotkey Adapter (`app/hotkeys.py`)

#### Purpose
Bridge between synchronous hotkey detection and asynchronous processing.

#### Architecture
- **Input**: `pynput` keyboard listener (runs in separate thread)
- **Output**: Async command queue via `loop.call_soon_threadsafe`
- **Thread Safety**: Isolated threading with proper async bridge

#### Key Mapping
```python
hotkey_mappings = {
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
```

#### Thread Safety Implementation
```python
def _on_release(self, key):
    # Detect key combination
    command = self._detect_command(key)
    if command:
        # Bridge to async context safely
        self._loop.call_soon_threadsafe(
            self.bus.commands.put_nowait, Command(command)
        )
```

### 2.5 HTTP API (`app/http_api.py`)

#### Purpose
RESTful API for user management and health monitoring.

#### Endpoints
- `GET /health` - Health check endpoint
- `POST /check_pdf` - Trigger PDF folder check
- `GET /set_user_id?user_id=username` - Set user ID
- `OPTIONS /set_user_id` - CORS preflight

#### CORS Configuration
```python
response.headers['Access-Control-Allow-Origin'] = 'http://150.1.6.144:8080'
response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
```

### 2.6 Command Handlers (`app/handlers.py`)

#### Purpose
Business logic and command processing engine.

#### Responsibilities
- Command interpretation and execution
- State management (minimal client state)
- Error handling and recovery
- Integration with external services

#### State Management
```python
# Minimal client state - server is source of truth
self.audio_state = {
    'is_playing': False,
    'current_file': 'audio.mp3',
    'position': 0,
    'duration': 180
}
```

#### Command Processing Loop
```python
async def run(self, stop_event: asyncio.Event):
    while not stop_event.is_set():
        try:
            cmd = await asyncio.wait_for(self.bus.commands.get(), timeout=1.0)
            await self._handle_command(cmd)
            self.bus.commands.task_done()
        except asyncio.TimeoutError:
            continue
        except Exception as e:
            print(f"❌ Error handling command: {e}")
```

### 2.7 Configuration (`app/config.py`)

#### Purpose
Centralized configuration management with type safety.

#### Sources
1. **TOML Files**: `app.toml` for default configuration
2. **Environment Variables**: Override TOML values
3. **Runtime Validation**: Type checking and validation

#### Configuration Schema
```python
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
```

### 2.8 Lifecycle Management (`app/lifecycle.py`)

#### Purpose
Application startup, shutdown, and task coordination.

#### Features
- **Graceful Shutdown**: Signal handling (SIGINT, SIGTERM)
- **Task Management**: Coordinated startup and shutdown
- **Resource Cleanup**: Automatic cleanup of all resources
- **Error Handling**: Comprehensive error recovery

#### Shutdown Sequence
```python
async def run_app(cfg: Config):
    # ... component initialization ...
    
    # Wait for stop signal
    await stop_event.wait()
    
    # Graceful teardown
    await ws.stop()
    await api.stop()
    
    # Cancel all tasks
    for t in tasks:
        t.cancel()
    
    # Wait for tasks to complete cancellation
    for t in tasks:
        with contextlib.suppress(asyncio.CancelledError):
            await t
```

---

## 3. Performance Specifications

### 3.1 Resource Requirements

| Resource | Minimum | Recommended | Maximum |
|----------|---------|-------------|---------|
| **Memory** | 50MB | 100MB | 200MB |
| **CPU** | 1 core | 2 cores | 4 cores |
| **Disk Space** | 10MB | 50MB | 100MB |
| **Network** | 1Mbps | 10Mbps | 100Mbps |

### 3.2 Performance Metrics

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| **Startup Time** | < 2 seconds | Time from process start to ready |
| **Hotkey Response** | < 50ms | Time from key press to command queued |
| **WebSocket Latency** | < 10ms local, < 100ms remote | Round-trip message time |
| **Memory Usage** | < 100MB | Peak memory consumption |
| **CPU Usage** | < 1% idle, < 5% active | Average CPU utilization |

### 3.3 Scalability Considerations

- **Concurrent Connections**: Single WebSocket connection per instance
- **File Monitoring**: Single directory, configurable pattern matching
- **Hotkey Processing**: Single listener, multiple key combinations
- **HTTP API**: Single server instance, multiple concurrent requests

---

## 4. Security Specifications

### 4.1 Data Protection

#### User Data
- **Storage**: Local JSON file (`user_data.json`)
- **Encryption**: Not encrypted (local storage only)
- **Access**: Read/write by application process only
- **Retention**: Persistent until manually deleted

#### Network Communication
- **Protocol**: WebSocket over TCP (TLS recommended for production)
- **Authentication**: User ID-based identification
- **Authorization**: Server-side validation
- **Data Validation**: All inputs validated and sanitized

### 4.2 Security Features

#### Input Validation
- **Hotkeys**: Whitelist of allowed key combinations
- **File Paths**: Restricted to configured directories
- **WebSocket Messages**: JSON schema validation
- **HTTP Requests**: Parameter validation and sanitization

#### Error Handling
- **Information Disclosure**: No sensitive data in error messages
- **Logging**: Structured logging without sensitive information
- **Recovery**: Graceful error recovery without data loss

#### Resource Protection
- **Memory Limits**: Bounded memory usage with cleanup
- **CPU Limits**: Efficient algorithms with timeout protection
- **File Access**: Minimal required permissions
- **Network Access**: Single WebSocket connection only

---

## 5. Testing Specifications

### 5.1 Testing Strategy

#### Unit Testing
- **Coverage Target**: 90%+ code coverage
- **Framework**: pytest
- **Scope**: Individual component testing
- **Mocking**: External dependencies mocked

#### Integration Testing
- **Scope**: Component interaction testing
- **Environment**: Test environment with mock server
- **Data**: Synthetic test data
- **Validation**: End-to-end workflow testing

#### Performance Testing
- **Load Testing**: Concurrent hotkey presses
- **Stress Testing**: High-frequency PDF processing
- **Memory Testing**: Long-running stability
- **Network Testing**: Connection failure scenarios

### 5.2 Test Cases

#### Critical Path Testing
1. **Application Startup**: All components initialize correctly
2. **Hotkey Processing**: Commands are processed within 50ms
3. **PDF Processing**: Files are detected and processed correctly
4. **WebSocket Communication**: Messages are sent and received
5. **Error Recovery**: Application recovers from network failures
6. **Graceful Shutdown**: All resources are cleaned up properly

#### Edge Case Testing
1. **Network Disconnection**: Auto-reconnect functionality
2. **Invalid PDF Files**: Error handling for corrupted files
3. **Permission Denied**: File access error handling
4. **Resource Exhaustion**: Memory and CPU limit testing
5. **Concurrent Operations**: Multiple simultaneous commands

---

## 6. Deployment Specifications

### 6.1 Environment Requirements

#### Development Environment
- **Python**: 3.8+ with asyncio support
- **Dependencies**: All packages from `requirements.txt`
- **Development Tools**: pytest, black, mypy
- **IDE Support**: VS Code, PyCharm, or equivalent

#### Production Environment
- **Python**: 3.11+ (recommended for performance)
- **Operating System**: Windows 10/11, macOS 10.15+, Linux
- **Service Management**: systemd (Linux), Windows Service
- **Monitoring**: Log monitoring and health checks

### 6.2 Installation Process

#### Manual Installation
```bash
# 1. Clone repository
git clone <repository-url>
cd native_app_v2

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure application
cp app.toml.example app.toml
# Edit app.toml with your settings

# 4. Test installation
python test.py

# 5. Run application
python main.py
```

#### Automated Installation
```bash
# Using pip (if published)
pip install audio-transcription-controller-v2

# Using Docker
docker run -d --name atc-v2 audio-transcription-controller-v2
```

### 6.3 Configuration Management

#### Configuration Sources (Priority Order)
1. **Environment Variables**: Highest priority
2. **TOML Files**: Default configuration
3. **Hardcoded Defaults**: Fallback values

#### Environment Variables
```bash
export WS_URL="ws://your-server:6790"
export PDF_DIR="/path/to/pdf/folder"
export HTTP_PORT="8080"
```

#### TOML Configuration
```toml
# app.toml
ws_url = "ws://150.1.6.144:6790"
pdf_dir = "./pdf_for_submission"
http_host = "127.0.0.1"
http_port = 8080
hotkey_stop = "f1"
hotkey_check_pdf = "f2"
pdf_glob = "*.pdf"
pdf_wait_window_s = 5
reconnect_base_s = 0.5
reconnect_max_s = 15.0
```

---

## 7. Monitoring and Observability

### 7.1 Logging Specifications

#### Log Levels
- **DEBUG**: Detailed diagnostic information
- **INFO**: General application flow
- **WARNING**: Potential issues
- **ERROR**: Error conditions
- **CRITICAL**: Critical failures

#### Log Format
```json
{
  "timestamp": "2024-12-01T10:30:00.000Z",
  "level": "INFO",
  "component": "ws_client",
  "message": "WebSocket connected",
  "data": {
    "url": "ws://150.1.6.144:6790",
    "reconnect_count": 0
  }
}
```

#### Log Rotation
- **Size Limit**: 10MB per file
- **File Count**: 5 files maximum
- **Compression**: gzip compression for old files
- **Retention**: 30 days

### 7.2 Metrics Collection

#### Performance Metrics
- **Response Time**: Hotkey to command processing time
- **Memory Usage**: Peak and average memory consumption
- **CPU Usage**: Average CPU utilization
- **Network Latency**: WebSocket round-trip time

#### Business Metrics
- **Command Frequency**: Hotkey usage patterns
- **PDF Processing**: File processing success rate
- **Error Rates**: Component error frequencies
- **Uptime**: Application availability

#### Health Metrics
- **Component Status**: Individual component health
- **Resource Utilization**: Memory, CPU, disk usage
- **Connection Status**: WebSocket connection health
- **File System**: PDF directory monitoring

---

## 8. Maintenance and Support

### 8.1 Maintenance Procedures

#### Regular Maintenance
- **Log Rotation**: Automatic log cleanup
- **Configuration Updates**: TOML file updates
- **Dependency Updates**: Security patches
- **Performance Monitoring**: Resource usage tracking

#### Troubleshooting Procedures
1. **Check Logs**: Review application logs for errors
2. **Verify Configuration**: Validate TOML and environment variables
3. **Test Components**: Run individual component tests
4. **Network Connectivity**: Verify WebSocket connection
5. **File Permissions**: Check PDF directory access

### 8.2 Support Information

#### Common Issues
1. **WebSocket Connection Failed**: Check server URL and network connectivity
2. **Hotkeys Not Working**: Verify pynput permissions and key mappings
3. **PDF Processing Failed**: Check file permissions and directory access
4. **High Memory Usage**: Monitor for memory leaks and restart if needed

#### Contact Information
- **Technical Support**: [support-email]
- **Bug Reports**: [bug-tracker-url]
- **Feature Requests**: [feature-request-url]
- **Documentation**: [documentation-url]

---

## 9. Version History and Migration

### 9.1 Version History

#### v1.0.0 (Original)
- Monolithic architecture
- Threading issues
- Manual resource management
- Basic error handling

#### v2.0.0 (Current)
- Async-first architecture
- Event-driven design
- Automatic resource management
- Comprehensive error handling
- Auto-reconnect functionality
- TOML configuration
- Modular components

### 9.2 Migration Guide

#### From v1 to v2
1. **Backup Configuration**: Save existing settings
2. **Install v2**: Install new version alongside v1
3. **Migrate Configuration**: Convert settings to TOML format
4. **Test Functionality**: Verify all features work correctly
5. **Switch Over**: Stop v1, start v2
6. **Monitor**: Watch for any issues

#### Configuration Migration
```python
# v1 (hardcoded)
ws_url = "ws://150.1.6.144:6790"

# v2 (TOML)
ws_url = "ws://150.1.6.144:6790"
```

#### Feature Compatibility
- **Hotkeys**: 100% compatible
- **WebSocket Protocol**: 100% compatible
- **PDF Processing**: 100% compatible
- **HTTP API**: 100% compatible

---

## 10. Future Enhancements

### 10.1 Planned Features

#### Short Term (v2.1)
- **Enhanced Logging**: Structured logging with correlation IDs
- **Metrics Export**: Prometheus metrics endpoint
- **Configuration Validation**: Runtime configuration validation
- **Health Checks**: Comprehensive health check endpoint

#### Medium Term (v2.2)
- **Plugin System**: Extensible command processing
- **Multiple WebSocket**: Support for multiple server connections
- **Advanced Hotkeys**: Custom hotkey combinations
- **GUI Configuration**: Graphical configuration interface

#### Long Term (v3.0)
- **Microservices**: Split into separate services
- **Cloud Integration**: Cloud-based configuration and monitoring
- **Mobile Support**: Mobile application companion
- **AI Integration**: Intelligent command suggestions

### 10.2 Technical Debt

#### Current Limitations
- **Single Process**: All components in one process
- **Limited Scalability**: Single WebSocket connection
- **Basic Monitoring**: Limited observability features
- **Manual Configuration**: No GUI configuration

#### Improvement Areas
- **Performance**: Further optimization opportunities
- **Security**: Enhanced security features
- **Usability**: Improved user experience
- **Maintainability**: Code quality improvements

---

## Conclusion

This technical specification provides comprehensive documentation for the Audio Transcription Controller v2, covering all aspects from architecture to deployment. The specification serves as a reference for developers, system administrators, and stakeholders involved in the development, deployment, and maintenance of the application.

The v2 architecture represents a significant improvement over v1, addressing all critical issues while maintaining full backward compatibility. The modular design, comprehensive error handling, and automatic resource management make it suitable for production deployment in professional environments.

