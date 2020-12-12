import os, re, time, json, requests
from bs4 import BeautifulSoup as bs
from urllib.parse import urljoin
from server import *


def get_json():

    session = requests.Session()

    # faking session
    session.headers["User-Agent"] = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36"

    # retrieving sporify playlist link
    url = input('Spotify playlist link:\n')

    html = session.get(url).content

    # beautify content
    soup = bs(html, "html.parser")

    # find script with Spotify.Entity json document
    script = soup.find('script', text=re.compile('Spotify\.Entity'))

    # extract json document
    json_text = re.search(r'^\s*Spotify\.Entity\s*=\s*({.*?})\s*;\s*$',
                          script.string, flags=re.DOTALL | re.MULTILINE).group(1)

    data = json.loads(json_text)

    return data


def import_playlist(access_token, user_id):

    # get playlist from spotify
    spotify_playlist = get_json()

    # extract name from spotify playlist
    new_playlist_name = spotify_playlist['name']

    # create a new deezer playlist with the same name of the spotify playlist
    deezer_playlist_id = requests.post(
        f'https://api.deezer.com/user/{user_id}/playlists/?title={new_playlist_name}&request_method=post&access_token={access_token}').json()['id']

    n_tracks = len(spotify_playlist['tracks']['items'])

    if n_tracks == 0:
        return

    print(f'Importing {n_tracks} from playlist {new_playlist_name}')

    input('Press any key to confirm or CTRL + C to exit')

    print('\nStarting...\n')

    not_found = []

    for record in spotify_playlist['tracks']['items']:

        # extract details from record
        artist_name = record['track']['artists'][0]['name']
        track_name = record['track']['name']

        # search deezer track by artist and song title
        r = requests.get(
            f'https://api.deezer.com/search?q=artist:"{artist_name}" track:"{track_name}"').json()

        try:
            print(f'Adding {artist_name} - {track_name}...')

            # if track not found
            if len(r['data']) == 0:

                # remove (feat. ...) and - feat from track title
                track_name = re.sub(pattern='\(.*', repl='', string=track_name)
                track_name = re.sub(pattern=' - feat.*',
                                    repl='', string=track_name)

                # search again
                r = requests.get(
                    f'https://api.deezer.com/search?q=artist:"{artist_name}" track:"{track_name}"').json()

            # pick best result
            track_id = r['data'][0]['id']

            # add to deezer playlist
            r = requests.post(
                f'https://api.deezer.com/playlist/{deezer_playlist_id}/tracks?songs={track_id}&request_method=post&access_token={access_token}')

        except IndexError:
            # if r['data'] is empty it raise IndexError
            not_found.append(f'{artist_name} - {track_name}')
            pass

    print('Operation completed: {} tracks added to {} Deezer playlist'.format(
        n_tracks - len(not_found), new_playlist_name))

    if len(not_found) > 0:
        print('\nTracks not found: ')
        for record in not_found:
            print(record)


def login():

    # starting server for oAuth 2.0 authentication process
    start_server()

    access_token = ''

    print('Waiting for login...')

    # when the access token is ready we will receive it in a file
    while not os.path.exists('token.txt'):
        time.sleep(1)

    # retrieves the access token from the file and deletes it
    with open('token.txt', 'r') as token_file:
        access_token = token_file.read()
        token_file.close()
        os.remove('token.txt')

    # shutdown oAuth server
    stop_server()

    # get user id
    user = requests.get(
        f'https://api.deezer.com/user/me?&access_token={access_token}').json()

    # if token is invalid or has expired user need to open again the link
    if 'error' in user:
        print('ERROR ' + user['error']['message'])
        return

    # extract user Id from user
    user_id = user['id']

    print('Logged in!\n')
    return (access_token, user_id)


def main():

    try:
        access_token, user_id = login()
        import_playlist(access_token, user_id)

    except KeyboardInterrupt:
        stop_server()
        quit('\nBye!\n')

    except requests.exceptions.MissingSchema as error:
        quit('ERROR ' + str(error))


if __name__ == "__main__":
    main()
