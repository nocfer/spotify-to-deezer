import requests
from deezer import DeezerOAuthHandler as handler
from pathlib import Path


class Deezer:
    def __init__(self):
        self.access_token = None
        self.user_id = None
        self.playlist_name = None
        self.deezer_playlist_id = None
        self.base_url = f"https://api.deezer.com"
        pass

    def login(self):

        print("Waiting for login...")
        try:
            token_file_path = Path("./token.txt")

            if not token_file_path.exists():
                access_token = handler.get_token()
                # starting server for oAuth 2.0 authentication process
            token_fp = token_file_path.open()
            access_token = token_fp.readline()
            access_token = access_token.split("&")[0]
            token_fp.close()
        except FileNotFoundError:
            print("ERROR: Token file not found.")

        print(f"retrieved token {access_token}")
        # get user id
        user = requests.get(
            f"https://api.deezer.com/user/me?&access_token={access_token}"
        ).json()

        print(f"user: {user} with token: {access_token}")

        # if token is invalid or has expired user need to open again the link
        if "error" in user:
            print("ERROR " + user["error"]["message"])
            return

        # extract user Id from user
        user_id = user["id"]

        self.access_token = access_token
        self.user_id = user_id

        print("Logged in!\n")

    def create_playlist(self, playlist_name: str):
        url = f"{self.base_url}/user/{self.user_id}/playlists/?title={playlist_name}&request_method=post&access_token={self.access_token}"
        playlists_array = self.get_user_playlist()

        for playlist in playlists_array:
            if playlist["title"] == playlist_name:
                self.deezer_playlist_id = playlist["id"]
                return
        print(f"POST: {url}")

        self.deezer_playlist_id = requests.post(url).json()["id"]

        self.playlist_name = playlist_name

    def search_song(self, artist_name: str, track_name: str):
        try:
            print(f"searching track {track_name} - {artist_name}")

            path = f"search?q=artist:'{artist_name}' track:'{track_name}'"

            r = self.get(path)
            if len(r["data"]) == 0:
                # remove (feat. ...) and - feat from track title
                track_name = re.sub(pattern="\(.*", repl="", string=track_name)
                track_name = re.sub(pattern=" - feat.*", repl="", string=track_name)

                # search again
                r = self.get(route, query_param)
            return r
        except Exception as e:
            print(e)

    def add_song(self, track_id):
        req_param = dict(songs=track_id)
        route = f"playlist/{self.deezer_playlist_id}/tracks"
        self.post(route=route)

    def get_user_playlist(self):
        # https://api.deezer.com/user/427723685/playlists
        url = f"{self.base_url}/user/{self.user_id}/playlists"
        r = requests.get(url).json()
        return r["data"]
