# 🎶🔥 SpotifyToDeezer 🔥🎶

Transfer all your playlists from Spotify to Deezer! 🎶

## Installation

```bash
# download the repo
git clone https://github.com/Fer99n/spotify-to-deezer.git <installation_dir>

cd <installation_dir>

# create a virtual environment
python3 -m venv venv

# activate venv (if you're on Windows this line could differ)
source venv/bin/activate

# install the required modules
pip install -r ./requirements.txt

# run
python3 main.py
```

## Instructions

### Set up Deezer

1. Visit [Deezer Developers](https://developers.deezer.com/login?redirect=/api)

2. login with your deezer credentials and go to "my apps"

3. create an application with application domain http://localhost:5000 and redirect url http://localhost:5000/callback

### Set up Spotify

1. Visit [Spotify Developers](https://developer.spotify.com/dashboard/)

2. login with your spotify credentials and click the "create an app" button

3. when visualizing your newly created app, click on edit settings

4. input http://localhost:5000/callback in the Redirect URIs section

### Set up config.ini

1. Open config.ini files

2. Replace the values

### Run

`python3 main.py`
