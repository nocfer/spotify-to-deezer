import requests
from pathlib import Path
import SpotifyOAuthHandler as handler


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

    def login(self):
        try:
            token_file_path = Path("./spotify_token.txt")

            if not token_file_path.exists():
                access_token = handler.main()
                # starting server for oAuth 2.0 authentication process
            token_fp = token_file_path.open()
            access_token = token_fp.readline()
            access_token = access_token.split("&")[0]
            print(f"Access_token {access_token}")
            token_fp.close()

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
        print(self.playlist_id)

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
        playlist_query = "name, tracks.items(total)"

        # set urls
        playlist_url = f"{base_url}?fields={playlist_query}"

        # execute requests
        r_playlist = requests.get(playlist_url, headers=self.auth_header).json()

        self.playlist_name = r_playlist["name"]

        print(f"Playlist name: {self.playlist_name}")

    def get_playlist_tracks(self, playlist_id: str = None, offset: int = 0):

        if not playlist_id:
            playlist_id = self.playlist_id
        base_url = f"https://api.spotify.com/v1/playlists/{playlist_id}"

        if offset > 0:
            print(f"Retrieving next {offset}")

        # set fields to query from spotify APIs
        tracks_query = "next,total,items(track(artists.name, name))"

        # set urls
        tracks_url = f"{base_url}/tracks?offset={offset}&fields={tracks_query}"

        # execute requests
        r_tracks = requests.get(tracks_url, headers=self.auth_header).json()

        # save an instance of the retrieved fields
        self.tracks = r_tracks["items"]
        self.n_tracks = r_tracks["total"]
        self.n_tracks_fetched = self.n_tracks_fetched + len(self.tracks)

        if r_tracks["next"]:
            self.next = r_tracks["next"]
            self.has_next = True
        else:
            self.next = None
            self.has_next = False
