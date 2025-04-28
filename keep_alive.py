import http.server
import socketserver
import threading

def run_web_server():
    # Создаем простой HTTP-сервер для поддержания проекта "проснувшимся"
    class MyHandler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"Bot is running!")
    
    # Запускаем сервер в отдельном потоке
    port = 3000  # Стандартный порт, который Glitch использует для веб-серверов
    httpd = socketserver.TCPServer(("", port), MyHandler)
    print(f"Serving at port {port}")
    httpd.serve_forever()

def keep_alive():
    # Запускаем веб-сервер в отдельном потоке
    server_thread = threading.Thread(target=run_web_server)
    server_thread.daemon = True
    server_thread.start()
