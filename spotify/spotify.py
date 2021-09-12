import requests, datetime
from pathlib import Path
from spotify import SpotifyOAuthHandler as handler


class Spotify:
    def __init__(self):
        self.playlist_id = None
        self.has_next = False
        self.next = None
        self.n_tracks = 0
        self.n_tracks_fetched = 0
        self.n_tracks_transfered = 0
        self.playlist_name = None
        self.tracks = None

        self.auth_header = None
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
        try:
            token_file_path = Path("./spotify_token.txt")

            if not token_file_path.exists():
                handler.get_token()

            access_token = self.read_token(token_file_path)

        except FileNotFoundError:
            print("ERROR: Token file not found.")

        self.auth_header = {"Authorization": f"Bearer {access_token}"}

    def set_playlist_id(self, url: str()):
        if "open.spotify" in url:
            if "?" in url:
                self.playlist_id = url.split("playlist/")[1].split("?")[0]
            else:
                self.playlist_id = url.split("playlist/")[1]
        elif ":playlist:" in url:
            self.playlist_id = url.split(":playlist:")[1]
        else:
            raise Exception("Wrong URL")

    def get_playlist_url(self, url: str = None):
        if not url:
            playlist_url = input("Spotify playlist link:\n")
        else:
            playlist_url = url
        self.set_playlist_id(playlist_url)

    def get_playlist(self, playlist_id: str = None):
        # https://open.spotify.com/playlist/6FMls6rmInujNCikuWcuEk?si=c7480112c403470f

        if not playlist_id:
            playlist_id = self.playlist_id

        base_url = f"https://api.spotify.com/v1/playlists/{playlist_id}"

        # set fields to query from spotify APIs
        playlist_query = "name, tracks.total"

        # set urls
        playlist_url = f"{base_url}?fields={playlist_query}"

        # execute requests
        r_playlist = requests.get(playlist_url, headers=self.auth_header).json()

        self.playlist_name = r_playlist["name"]
        self.n_tracks = r_playlist["tracks"]["total"]
        print(f"Got playlist '{self.playlist_name}' with {self.n_tracks} songs")

    def get_playlist_tracks(self, playlist_id: str = None, offset: int = 0):

        if not playlist_id:
            playlist_id = self.playlist_id
        base_url = f"https://api.spotify.com/v1/playlists/{playlist_id}"

        # set fields to query from spotify APIs
        tracks_query = "next,items(track(artists.name, name))"

        # set urls
        tracks_url = f"{base_url}/tracks?offset={offset}&fields={tracks_query}"

        # execute requests
        r_tracks = requests.get(tracks_url, headers=self.auth_header).json()

        # save an instance of the retrieved fields
        self.tracks = r_tracks["items"]
        self.n_tracks_fetched = self.n_tracks_fetched + len(self.tracks)

        if r_tracks["next"]:
            self.next = r_tracks["next"]
            self.has_next = True
        else:
            self.next = None
            self.has_next = False
