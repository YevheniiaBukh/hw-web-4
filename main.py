import json
import socket
import threading
import mimetypes

from pathlib import Path
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import  parse_qs
from datetime import datetime


BASE_DIR = Path(__file__).resolve().parent
TEMPLATE_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"
STORAGE_DIR = BASE_DIR / "storage"
DATA_FILE = STORAGE_DIR / "data.json"


def socket_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.bind(("localhost", 5000))
    print("Сервер запущено на порту 5000")
    
    
    while True:
        data = server.recvfrom(1024)
        message = json.loads(data.decode("utf-8"))
        message_dict = json.loads(message)
        
        datetime = str(datetime.now())
        
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            messages = json.load(file)
            
    
        messages[datetime] = message_dict
        
        
        with open(DATA_FILE, "w", encoding="utf-8") as file:
            json.dump(messages, file, ensure_ascii=False, indent=4)
            
        print(f"Отримано повідомлення: {message_dict}")
 
        
class MyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.path = "/index.html"
            
        if self.path in ["/index.html", "/message.html", "/error.html"]:
            file_path = TEMPLATE_DIR / self.path.lstrip("/")
            content_type = "text/html"
            
        elif self.path in ["/style.css", "/logo.png"]:
            file_path = STATIC_DIR / self.path.lstrip("/")
            content_type, _ = mimetypes.guess_type(str(file_path))
            
        else:
            file_path = TEMPLATE_DIR / "error.html"
            content_type = "text/html"
            
        with open(file_path, "rb") as file:
            content = file.read()
            
        
        self.send_response(200)
        self.send_header("Content-type", content_type or "text/html")
        self.end_headers()   
        self.wfile.write(content)
    
    
    def do_POST(self):
        if self.path == "/message":
            count_lenght = int(self.headers["Content-Length"])
            data = self.rfile.read(count_lenght)
            body = data.decode("utf-8")
            
            parsed_data = parse_qs(body)
            
            username = parsed_data.get("username", [""])[0]
            message = parsed_data.get("message", [""])[0]
            
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            new_message = {
                "username": username,
                "message": message,
                "timestamp": timestamp
            }
             
            data_file = Path(__file__).parent / "storage" / "data.json"
            
            with open(data_file, "r", encoding="utf-8") as file:
                messages = json.load(file)

            messages.append(new_message)

            with open(data_file, "w", encoding="utf-8") as file:
                json.dump(messages, file, ensure_ascii=False, indent=4)

            print(f"Отримано повідомлення: {new_message}")
            
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Message received!")


def run_server():
    server = HTTPServer(("localhost", 3000), MyHandler)
    print("HTTP сервер запущено: http://localhost:3000")        
    server.serve_forever()


if __name__ == "__main__":
    socket_thread = threading.Thread(target=socket_server, daemon=True)
    socket_thread.start()
    run_server()
