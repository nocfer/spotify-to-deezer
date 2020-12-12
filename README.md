# 🎶🔥 SpotifyToDeezer 🔥🎶
Transfer all your playlists from Spotify to Deezer! 🎶

## Installation
```bash
# download the repo
git clone https://github.com/Fer99n/spotify-to-deezer.git <installation_dir>

cd <installation_dir>

# create a virtual environment
python3 -m virtualenv -p python3 venv

# activate venv (if you're on Windows this line could differ)
source venv/bin/activate

# install the required modules
pip install -r ./requirements.txt

# run
python3 main.py
```

## Instructions

1. Visit [Deezer Developers](https://developers.deezer.com/login?redirect=/api)

2. login with your deezer credentials and go to "my apps"

3. create an application with application domain http://localhost:5000 and redirect url http://localhost:5000/callback

4. once the application is created open oAuth.py and replace **app_id** and **secret** fields with the ones just generated

5. ```python3 main.py```