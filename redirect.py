import os

from bottle import redirect, run, route

PORT = int(os.environ["PORT"])

NEW_SITE = 'https://pebbleshows.herokuapp.com/pebbleConfig'


@route('<:re:.*>')
def all():
    redirect(NEW_SITE)

if __name__ == "__main__":
    print(PORT)
    run(host='0.0.0.0', port=PORT)
