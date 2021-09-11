import threading, requests, webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer

server_address = ("127.0.0.1", 5000)
event_get_token = threading.Event()

authorization_base_url = (
    "https://connect.deezer.com/oauth/auth.php?perms=manage_library"
)
redirect_uri = "http://localhost:5000/callback"

# Change these with yours
secret = ""
app_id = ""

auth_URL = f"{authorization_base_url}&app_id={app_id}&redirect_uri={redirect_uri}"

access_token = ""


class DeezerOAuthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
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

            if "/callback" in self.path:
                print("callback received")
                code = self.path.split("?")[1].split("=")[1]
                # save the token in a txt file so we can terminate the server thread
                r = requests.get(
                    f"https://connect.deezer.com/oauth/access_token.php?app_id={app_id}&secret={secret}&code={code}"
                )
                print(r.text)
                access_token = r.text.split("=")[1]
                token_file = open("token.txt", "w")
                token_file.write(access_token)
                token_file.close()
                print(f"Code: {access_token}")
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

        if event_get_token.wait(10):
            server.shutdown()
            server.server_close()
            return str(access_token)

    except KeyboardInterrupt:
        exit()


if __name__ == "__main__":
    get_token()
