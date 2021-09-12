import requests, datetime
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

    def read_token(self, token_file_path):
        token_fp = open(token_file_path, "r")
        line = token_fp.readline()
        splits = line.split("&")
        timestamp = splits[1]
        saved_at = datetime.datetime.fromtimestamp(float(timestamp))
        diff = datetime.datetime.now() - saved_at
        access_token = splits[0]
        token_fp.close()

        if diff > datetime.timedelta(hours=1):
            handler.get_token()
            self.read_token(token_file_path)
            return None

        return access_token

    def login(self):

        print("Waiting for login...")
        try:
            token_file_path = Path("./deezer_token.txt")

            if not token_file_path.exists():
                handler.get_token()

            access_token = self.read_token(token_file_path)

        except FileNotFoundError:
            print("ERROR: Token file not found.")

        print(f"retrieved token {access_token}")
        # get user id
        user = requests.get(
            f"https://api.deezer.com/user/me?&access_token={access_token}"
        ).json()

        # if token is invalid or has expired user need to open again the link
        if "error" in user:
            print("ERROR " + user["error"]["message"])
            return

        # extract user Id from user
        user_id = user["id"]

        self.access_token = access_token
        self.user_id = user_id

        print(f"Hi {user['firstname']}, you are now logged in!\n")

    def create_playlist(self, playlist_name: str):
        url = f"{self.base_url}/user/{self.user_id}/playlists/?title={playlist_name}&request_method=post&access_token={self.access_token}"
        playlists_array = self.get_user_playlist()

        for playlist in playlists_array:
            if playlist["title"] == playlist_name:
                self.deezer_playlist_id = playlist["id"]
                self.playlist_name = playlist_name

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

    def add_song(self, track_ids):
        id_list = ""
        for t_id in track_ids:
            id_list = f"{id_list}{t_id},"
            # add to deezer playlist
            r = requests.post(
                f"{self.base_url}/playlist/{self.deezer_playlist_id}/tracks?songs={id_list}&request_method=post&access_token={self.access_token}"
            )

    def get_user_playlist(self):
        # https://api.deezer.com/user/427723685/playlists
        url = f"{self.base_url}/user/{self.user_id}/playlists"
        r = requests.get(url).json()
        return r["data"]
