#!/usr/bin/python
# -*- coding: utf-8 -*-


import json
import urllib
import os

import bottle as app
import rauth

# import config

TRAKTV_CLIENT_ID = os.environ.get("TRAKTV_CLIENT_ID")
TRAKTV_CLIENT_SECRET = os.environ.get("TRAKTV_CLIENT_SECRET")
PORT = os.environ.get("PORT", 8080)

BASE_URL = "http://traktv-forwarder.herokuapp.com/"

oauth2 = rauth.OAuth2Service
traktv = oauth2(
    client_id=TRAKTV_CLIENT_ID,
    client_secret=TRAKTV_CLIENT_SECRET,
    name='traktv',
    authorize_url='https://api-v2launch.trakt.tv/oauth/authorize',
    access_token_url="https://api-v2launch.trakt.tv/oauth/token",
    base_url="https://api-v2launch.trakt.tv",
)
common_headers = {
    "trakt-api-version": 2,
    "trakt-api-key": TRAKTV_CLIENT_ID,
}

redirect_uri = BASE_URL + "success"


@app.route('/')
def index():
    app.redirect("/login")
    # return '<a href="/login">Log in using traktv</a>'


@app.route('/login<:re:/?>')
def login():
    params = dict(
        response_type='code',
        redirect_uri=redirect_uri
    )
    url = traktv.get_authorize_url(**params)
    print("url:", url)

    app.redirect(url)


@app.route('/success<:re:/?>')
def login_success():
    if app.request.params.get('error'):
        return "An error occoured. Please try again."
    code = app.request.params.get('code')

    # session = traktv.get_auth_session(
    #     data=dict(
    #         code=code,
    #         redirect_uri=redirect_uri,
    #         grant_type='authorization_code'
    #     ),
    #     decoder=json.loads
    # )
    access_token = traktv.get_access_token(
        data=dict(
            code=code,
            redirect_uri=redirect_uri,
            grant_type='authorization_code'
        ),
        decoder=json.loads
    )
    payload = {'accessToken': access_token}
    print("Access token:", access_token)
    redirect = "pebblejs://close#" + urllib.quote(json.dumps(payload))
    print("Redirecting to: ", redirect)

    app.redirect(redirect)


# @app.route('/info<:re:/?>')
# def info():
#     access_token = app.request.params.get('accessToken')

#     session = traktv.get_session(access_token)
#     json_path = "https://api-v2launch.trakt.tv/users/youtux/watched/shows"
#     session_get = session.get(json_path, json=True, headers=common_headers)

#     return session_get.content

if __name__ == "__main__":
    app.run(
        port=PORT,
        host="0.0.0.0",
        debug=True,
        reloader=True,
    )
