from deezer.deezer import Deezer
from spotify.spotify import Spotify
import requests, re


def main():
    try:
        print("Setup phase...")
        deezer = Deezer()
        spotify = Spotify()

        # login
        deezer.login()
        print("Deezer login successful")
        spotify.login()
        print("Spotify login successful\n")

        # ask for user to input the playlist url
        spotify.get_playlist_url()

        # fetch playlist data
        spotify.get_playlist()

        spotify.get_playlist_tracks(offset=0)

        # create deezer playlist
        deezer.create_playlist(spotify.playlist_name)

        not_found = []
        track_ids = []
        offset = 0
        while spotify.n_tracks_transfered == 0 or spotify.has_next:
            for track in spotify.tracks:
                artist = track["track"]["artists"][0]["name"]
                title = track["track"]["name"]
                # search deezer track by artist and song title
                r = requests.get(
                    f'{deezer.base_url}/search?q=artist:"{artist}" track:"{title}"'
                ).json()

                try:
                    # if track not found
                    if len(r["data"]) == 0:

                        # remove (feat. ...) and - feat from track title
                        title = re.sub(pattern="\(.*", repl="", string=title)
                        title = re.sub(pattern=" - feat.*", repl="", string=title)

                        # search again
                        r = requests.get(
                            f'https://api.deezer.com/search?q=artist:"{artist}" track:"{title}"'
                        ).json()

                    # pick best result
                    track_ids.append(r["data"][0]["id"])

                    print(f"[{spotify.n_tracks_transfered}] + {artist} - {title}...")

                    tracks_left = spotify.n_tracks - spotify.n_tracks_transfered - 1

                    if len(track_ids) == 50 or tracks_left == 0:
                        print("-------------Adding song-------------")
                        deezer.add_song(track_ids)
                        track_ids.clear()

                    spotify.n_tracks_transfered += 1

                except IndexError:
                    not_found.append(f"{artist} - {title}")
                    pass

            if spotify.has_next:
                offset = offset + 100
                spotify.get_playlist_tracks(offset=offset)
        print(
            "Operation completed: {} tracks added to {} Deezer playlist".format(
                spotify.n_tracks - len(not_found), deezer.playlist_name
            )
        )

        if len(not_found) > 0:
            print("\nTracks not found: ")
            for record in not_found:
                print(record)

    except KeyboardInterrupt:
        exit()
    except Exception as e:
        print(e)
    exit()


if __name__ == "__main__":
    main()
