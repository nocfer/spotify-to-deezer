import threading, requests, webbrowser, configparser
from http.server import BaseHTTPRequestHandler, HTTPServer
import datetime

server_address = ("127.0.0.1", 5000)
event_get_token = threading.Event()

config = configparser.ConfigParser()
config.read("config.ini")

authorization_base_url = (
    "https://connect.deezer.com/oauth/auth.php?perms=manage_library"
)
redirect_uri = "http://localhost:5000/callback"

app_id = config["DEEZER"]["DEEZER_APP_ID"]
secret = config["DEEZER"]["DEEZER_SECRET"]

auth_URL = f"{authorization_base_url}&app_id={app_id}&redirect_uri={redirect_uri}"

access_token = ""


class DeezerOAuthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()

            self.wfile.write(
                bytes("<html><head><title>Callback received</title></head>", "utf-8")
            )
            self.wfile.write(bytes("<body>", "utf-8"))
            self.wfile.write(bytes("<p>You can close this tab.</p>", "utf-8"))
            self.wfile.write(bytes("</body></html>", "utf-8"))

            if "/callback" in self.path:
                code = self.path.split("?")[1].split("=")[1]
                # save the token in a txt file so we can terminate the server thread
                r = requests.get(
                    f"https://connect.deezer.com/oauth/access_token.php?app_id={app_id}&secret={secret}&code={code}"
                )
                access_token = r.text.split("=")[1].split("&")[0]
                token_file = open("deezer_token.txt", "w")
                line = f"{access_token}&{datetime.datetime.now().timestamp()}"
                token_file.write(line)
                token_file.close()
                event_get_token.set()
            return
        except Exception as e:
            print(e)


def get_token():
    try:
        server = HTTPServer(server_address, DeezerOAuthHandler)
        thread1 = threading.Thread(name="server", target=server.serve_forever)
        thread1.start()

        webbrowser.open(auth_URL, new=0)

        event_get_token.wait(10)
        server.shutdown()
        server.server_close()

    except KeyboardInterrupt:
        exit()


if __name__ == "__main__":
    get_token()
