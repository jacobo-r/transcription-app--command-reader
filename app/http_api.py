import asyncio
import json
import os
from aiohttp import web
from .bus import Bus, Command

class HTTPAPI:
    def __init__(self, bus: Bus, host: str, port: int):
        self.bus = bus
        self.host = host
        self.port = port
        self._runner = None
        self._site = None
        self.user_id = None
        self.user_data_file = "user_data.json"
        self.load_user_id()

    async def start(self):
        app = web.Application()
        app.add_routes([
            web.get("/health", self.health),
            web.post("/check_pdf", self.check_pdf),
            web.get("/set_user_id", self.set_user_id_handler),
            web.options("/set_user_id", self.options_handler),
        ])
        self._runner = web.AppRunner(app)
        await self._runner.setup()
        self._site = web.TCPSite(self._runner, self.host, self.port)
        await self._site.start()
        print(f"🌐 HTTP server started on http://{self.host}:{self.port}")
        print("📡 Endpoint: GET /set_user_id?user_id=username")
        print("🌐 CORS enabled for: http://150.1.6.144:8080")
        
        # Keep task alive
        while True:
            await asyncio.sleep(3600)

    async def stop(self):
        if self._site:
            await self._site.stop()
        if self._runner:
            await self._runner.cleanup()

    async def health(self, _):
        return web.json_response({"ok": True})

    async def check_pdf(self, _):
        await self.bus.commands.put(Command("check_pdf_folder"))
        return web.json_response({"queued": True})

    def load_user_id(self):
        """Load user ID from JSON file"""
        try:
            if os.path.exists(self.user_data_file):
                with open(self.user_data_file, 'r') as f:
                    data = json.load(f)
                    self.user_id = data.get('user_id')
                    if self.user_id:
                        print(f"👤 Loaded user ID: {self.user_id}")
        except Exception as e:
            print(f"❌ Error loading user ID: {e}")

    def save_user_id(self, user_id):
        """Save user ID to JSON file"""
        try:
            self.user_id = user_id
            data = {'user_id': user_id}
            with open(self.user_data_file, 'w') as f:
                json.dump(data, f)
            print(f"👤 User ID saved: {user_id}")
        except Exception as e:
            print(f"❌ Error saving user ID: {e}")

    async def set_user_id_handler(self, request):
        """HTTP handler for setting user ID"""
        try:
            user_id = request.query.get('user_id')
            
            if not user_id:
                response = web.json_response({'error': 'user_id query parameter is required'}, status=400)
            else:
                self.save_user_id(user_id)
                response = web.json_response({'success': True, 'user_id': user_id})
            
            # Add CORS headers
            response.headers['Access-Control-Allow-Origin'] = 'http://150.1.6.144:8080'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
            
            return response
            
        except Exception as e:
            response = web.json_response({'error': str(e)}, status=500)
            response.headers['Access-Control-Allow-Origin'] = 'http://150.1.6.144:8080'
            return response

    async def options_handler(self, request):
        """Handle OPTIONS requests for CORS preflight"""
        response = web.Response()
        response.headers['Access-Control-Allow-Origin'] = 'http://150.1.6.144:8080'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response



