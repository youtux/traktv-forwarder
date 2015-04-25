#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import os

import bottle as app
import rauth

from six.moves.urllib import parse

from pin_database import PinDatabase

# import config

TRAKTV_CLIENT_ID = os.environ["TRAKTV_CLIENT_ID"]
TRAKTV_CLIENT_SECRET = os.environ["TRAKTV_CLIENT_SECRET"]
PEBBLE_TIMELINE_API_KEY = os.environ["PEBBLE_TIMELINE_API_KEY"]
MONGODB_URL = os.environ["MONGODB_URL"]
PORT = os.environ["PORT"]

TRAKTTV_BASE_URL = "http://traktv-forwarder.herokuapp.com"

oauth2 = rauth.OAuth2Service
traktv = oauth2(
    client_id=TRAKTV_CLIENT_ID,
    client_secret=TRAKTV_CLIENT_SECRET,
    name='traktv',
    authorize_url='https://trakt.tv/oauth/authorize',
    access_token_url="https://trakt.tv/oauth/token",
    base_url="https://trakt.tv",
)
common_headers = {
    "trakt-api-version": 2,
    "trakt-api-key": TRAKTV_CLIENT_ID,
}

redirect_uri = TRAKTTV_BASE_URL + "/success"

pin_db = PinDatabase(MONGODB_URL)


@app.route('/')
def index():
    # app.redirect("/login")
    return app.static_file("index.html", root='.')


@app.route('/login<:re:/?>')
def login():
    params = dict(
        response_type='code',
        redirect_uri=redirect_uri
    )
    url = traktv.get_authorize_url(**params)
    print("url:", url)

    app.redirect(url)


def json_dec(s):
    if isinstance(s, bytes):
        s = s.decode('utf8')
    return json.loads(s)

@app.route('/success<:re:/?>')
def login_success():
    if app.request.params.get('error'):
        return "An error occoured. Please try again."
    code = app.request.params.get('code')

    access_token = traktv.get_access_token(
        data=dict(
            code=code,
            redirect_uri=redirect_uri,
            grant_type='authorization_code'
        ),
        decoder=json_dec
    )
    payload = {'accessToken': access_token}
    print("Access token:", access_token)
    redirect = "pebblejs://close#" + parse.quote(json.dumps(payload))
    print("Redirecting to: ", redirect)

    app.redirect(redirect)


@app.route('/api/getLaunchData/<launch_code:int>')
def get_launch_data(launch_code):
    """{action: "check-in", episode: {}}"""
    """{action: "mark-as-seen", episode: {}}"""
    # Fetch pin from database
    try:
        pin_obj = pin_db.pin_for_launch_code(launch_code)
    except KeyError as e:
        return json.dumps({'error': str(e)})

    pin, metadata = pin_obj['pin'], pin_obj['metadata']

    episode_id = metadata['episodeID']

    for pin_action in pin['actions']:
        if pin_action['launchCode'] == launch_code:
            break
    if pin_action["title"] == "Mark as seen":
        action = "markAsSeen"
    elif pin_action["title"] == "Check-in":
        action = "checkIn"
    else:
        raise ValueError("Pin action unknown")

    return json.dumps({
        'episodeID': metadata['episodeID'],
        'action': action,
    })

    return json.dumps({episode_id: episode_id})

if __name__ == "__main__":
    app.run(
        server='cherrypy',
        port=PORT,
        host="0.0.0.0",
        debug=True,
        # reloader=True,
    )
