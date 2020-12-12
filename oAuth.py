import os, requests
from flask import Flask, request, redirect

app = Flask(__name__)

authorization_base_url = 'https://connect.deezer.com/oauth/auth.php?perms=manage_library'
token_url = 'https://connect.deezer.com/oauth/access_token.php'
redirect_uri = 'http://localhost:5000/callback'
secret = '<SECRET>' 
app_id = '<APP_ID>'

# use plain HTTP callback
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = "1"


@ app.route("/", methods=["GET"])
def base():
    # building user login url
    auth_URL = f'{authorization_base_url}&app_id={app_id}&redirect_uri={redirect_uri}'
    return redirect(auth_URL)


@ app.route("/callback", methods=["GET"])
def callback():

    # getting autorization code from request parameter
    code = request.args.get('code')

    # building the URL that will return the access_token
    access_token_URL = f"{token_url}?app_id={app_id}&secret={secret}&code={code}"

    r = requests.get(access_token_URL)

    # extracting token
    access_token = r.text.split('=')[1]

    # save the token in a txt file so we can terminate the server thread
    with open('token.txt', 'w') as token_file:
        token_file.write(access_token)

    return 'Success! You can close this tab'
