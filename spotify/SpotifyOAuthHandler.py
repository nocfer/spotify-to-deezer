import threading, requests, webbrowser, configparser
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse
import base64


server_address = ("127.0.0.1", 5000)
event_get_token = threading.Event()

config = configparser.ConfigParser()
config.read("config.ini")

redirect_uri = "http://localhost:5000/callback"

# Change these with yours
secret = config["SPOTIFY"]["SPOTIFY_CLIENT_SECRET"]
app_id = config["SPOTIFY"]["SPOTIFY_CLIENT_ID"]

access_token = ""


class SpotifyOAuthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            self.write_get_response()
            if "/callback" in self.path:
                self.handle_callback()
            return
        except Exception as e:
            event_get_token.set()
            print(e)

    def handle_callback(self):
        code = self.path.split("?")[1].split("=")[1]
        print(self.path)
        print(code)
        self.get_token(code)

    def write_get_response(self):
        print("GET request received")
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

        self.wfile.write(
            bytes("<html><head><title>Callback received</title></head>", "utf-8")
        )
        self.wfile.write(bytes("<body>", "utf-8"))
        self.wfile.write(bytes("<p>You can close this tab.</p>", "utf-8"))
        self.wfile.write(bytes("</body></html>", "utf-8"))

    def get_token(self, code: str):
        base_url = "https://accounts.spotify.com/api/token"
        body = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
            "client_id": app_id,
            "client_secret": secret,
        }
        r = requests.post(base_url, data=body).json()

        self.save_token(r["access_token"])

    def save_token(self, access_token):
        token_file = open("spotify_token.txt", "w")
        token_file.write(access_token)
        token_file.close()
        event_get_token.set()
        access_token = access_token


def set_req_params(params: dict):
    tmp = "?"
    for key, value in params.items():
        tmp = f"{tmp}&{key}={value}"

    return tmp


def main():
    try:
        server = HTTPServer(server_address, SpotifyOAuthHandler)
        thread1 = threading.Thread(name="server", target=server.serve_forever)
        thread1.start()

        base_url = "https://accounts.spotify.com/authorize"
        req_params = {
            "client_id": app_id,
            "response_type": "code",
            "redirect_uri": redirect_uri,
        }

        url = f"{base_url}{set_req_params(req_params)}"

        print(url)
        webbrowser.open(url, new=0)

        if event_get_token.wait(10):
            server.shutdown()
            server.server_close()
            return access_token
    except KeyboardInterrupt:
        exit()


if __name__ == "__main__":
    main()
