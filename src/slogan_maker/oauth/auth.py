from flask import Flask, redirect, request, url_for, session
from requests_oauthlib import OAuth1Session

app = Flask(__name__)
app.secret_key = 'WPL_AP0.xkoOw3MkkyIsLUGK.MzY3Njc3ODk4Ng=='

# Replace these with your actual values from Twitter Developer dashboard
CONSUMER_KEY = 'UyFOKWneZpfrTGn67fuEkIKmL'
CONSUMER_SECRET = '78u2dg4k29vdi3'
REQUEST_TOKEN_URL = 'https://api.twitter.com/oauth/request_token'
AUTHORIZATION_URL = 'https://api.twitter.com/oauth/authorize'
ACCESS_TOKEN_URL = 'https://api.twitter.com/oauth/access_token'
CALLBACK_URL = 'http://127.0.0.1:5000/auth/twitter/callback'

@app.route('/')
def home():
    return 'Welcome to the Twitter OAuth example!'

@app.route('/login')
def login():
    twitter = OAuth1Session(CONSUMER_KEY, client_secret=CONSUMER_SECRET, callback_uri=CALLBACK_URL)
    fetch_response = twitter.fetch_request_token(REQUEST_TOKEN_URL)
    session['resource_owner_key'] = fetch_response.get('oauth_token')
    session['resource_owner_secret'] = fetch_response.get('oauth_token_secret')
    authorization_url = twitter.authorization_url(AUTHORIZATION_URL)
    return redirect(authorization_url)

@app.route('/auth/twitter/callback')
def callback():
    oauth_token = request.args.get('oauth_token')
    oauth_verifier = request.args.get('oauth_verifier')
    twitter = OAuth1Session(CONSUMER_KEY,
                            client_secret=CONSUMER_SECRET,
                            resource_owner_key=session['resource_owner_key'],
                            resource_owner_secret=session['resource_owner_secret'],
                            verifier=oauth_verifier)
    oauth_tokens = twitter.fetch_access_token(ACCESS_TOKEN_URL)
    session['access_token'] = oauth_tokens['oauth_token']
    session['access_token_secret'] = oauth_tokens['oauth_token_secret']
    return 'Authentication successful!'

if __name__ == '__main__':
    app.run(debug=True)