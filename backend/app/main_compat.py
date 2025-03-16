import os
import json
import uvicorn
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Mock data for surveys
MOCK_SURVEYS = [
    {
        "id": "1",
        "title": "Customer Satisfaction Survey",
        "description": "Please help us improve our services by answering a few questions",
        "status": "approved",
        "form_url": "https://docs.google.com/forms/d/e/example1",
        "created_at": "2025-03-15T10:00:00",
        "updated_at": "2025-03-15T11:00:00"
    },
    {
        "id": "2",
        "title": "Product Feedback Survey",
        "description": "We value your opinion on our product",
        "status": "draft",
        "form_url": "https://docs.google.com/forms/d/e/example2",
        "created_at": "2025-03-14T15:30:00",
        "updated_at": "2025-03-14T16:00:00"
    }
]

# Simple HTTP server to handle requests
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse

class APIHandler(BaseHTTPRequestHandler):
    def _send_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", os.getenv("FRONTEND_URL", "http://localhost:3000"))
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS, DELETE")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Credentials", "true")
        
    def _send_json_response(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-type", "application/json")
        self._send_cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
        
    def do_OPTIONS(self):
        self.send_response(200)
        self._send_cors_headers()
        self.end_headers()
        
    def do_GET(self):
        path = self.path
        
        # Root endpoint
        if path == "/":
            self._send_json_response({
                "message": "Welcome to the Google Forms Creation API",
                "debug_mode": os.getenv("DEBUG_MODE", "False").lower() == "true",
                "version": "1.0.0"
            })
            
        # List surveys endpoint
        elif path == "/api/surveys/":
            self._send_json_response({"surveys": MOCK_SURVEYS})
            
        # Get survey by ID endpoint
        elif path.startswith("/api/surveys/") and len(path.split("/")) == 4:
            survey_id = path.split("/")[3]
            survey = next((s for s in MOCK_SURVEYS if s["id"] == survey_id), None)
            
            if survey:
                self._send_json_response(survey)
            else:
                self._send_json_response({"detail": f"Survey with ID {survey_id} not found"}, 404)
                
        else:
            self._send_json_response({"detail": "Not Found"}, 404)
    
    def do_POST(self):
        path = self.path
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length).decode('utf-8')
        
        try:
            data = json.loads(post_data) if post_data else {}
        except json.JSONDecodeError:
            data = {}
            
        # Create survey endpoint
        if path == "/api/surveys/":
            # Generate a simple ID for the new survey
            new_id = str(len(MOCK_SURVEYS) + 1)
            new_survey = {
                "id": new_id,
                "title": data.get("title", "New Survey"),
                "description": data.get("description", ""),
                "status": "draft",
                "form_url": f"https://docs.google.com/forms/d/e/example{new_id}",
                "created_at": "2025-03-15T12:00:00",
                "updated_at": "2025-03-15T12:00:00"
            }
            
            MOCK_SURVEYS.append(new_survey)
            self._send_json_response(new_survey, 201)
            
        # Approve survey endpoint
        elif path.startswith("/api/surveys/") and path.endswith("/approve"):
            parts = path.split("/")
            if len(parts) == 5:
                survey_id = parts[3]
                survey = next((s for s in MOCK_SURVEYS if s["id"] == survey_id), None)
                
                if survey:
                    survey["status"] = "approved"
                    survey["updated_at"] = "2025-03-15T13:00:00"
                    self._send_json_response(survey)
                else:
                    self._send_json_response({"detail": f"Survey with ID {survey_id} not found"}, 404)
            else:
                self._send_json_response({"detail": "Not Found"}, 404)
                
        else:
            self._send_json_response({"detail": "Not Found"}, 404)
    
    def do_DELETE(self):
        path = self.path
        
        # Delete survey endpoint
        if path.startswith("/api/surveys/") and len(path.split("/")) == 4:
            survey_id = path.split("/")[3]
            survey_index = next((i for i, s in enumerate(MOCK_SURVEYS) if s["id"] == survey_id), None)
            
            if survey_index is not None:
                # Mark as deleted instead of removing
                MOCK_SURVEYS[survey_index]["status"] = "deleted"
                self.send_response(204)
                self._send_cors_headers()
                self.end_headers()
            else:
                self._send_json_response({"detail": f"Survey with ID {survey_id} not found"}, 404)
                
        else:
            self._send_json_response({"detail": "Not Found"}, 404)

# Run the server
def main():
    port = 8000
    server_address = ("0.0.0.0", port)
    httpd = HTTPServer(server_address, APIHandler)
    print(f"Starting server on http://0.0.0.0:{port}")
    httpd.serve_forever()

if __name__ == "__main__":
    main() 