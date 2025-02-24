# (c) Code-x-Mania

from os import getenv, environ
from dotenv import load_dotenv

load_dotenv("config.env", override=True)

class Var(object):
    API_ID = int(getenv('API_ID'))
    API_HASH = str(getenv('API_HASH'))
    BOT_TOKEN = str(getenv('BOT_TOKEN'))
    SESSION_NAME = str(getenv('SESSION_NAME', 'YasirRoBot'))
    SLEEP_THRESHOLD = int(getenv('SLEEP_THRESHOLD', '60'))
    WORKERS = int(getenv('WORKERS', '8'))
    BIN_CHANNEL = int(getenv('BIN_CHANNEL'))
    PORT = int(getenv('PORT', 80))
    BIND_ADRESS = str(getenv('WEB_SERVER_BIND_ADDRESS', '0.0.0.0'))
    PING_INTERVAL = int(environ.get("PING_INTERVAL", "1200"))  # 20 minutes
    OWNER_ID = int(getenv('OWNER_ID', '617426792'))
    NO_PORT = bool(getenv('NO_PORT', False))
    APP_NAME = None
    OWNER_USERNAME = str(getenv('OWNER_USERNAME'))
    if 'DYNO' in environ:
        ON_HEROKU = True
        APP_NAME = str(getenv('APP_NAME'))
    else:
        ON_HEROKU = False
    FQDN = (
        str(getenv('FQDN', BIND_ADRESS))
        if not ON_HEROKU or getenv('FQDN')
        else f'{APP_NAME}.herokuapp.com'
    )

    URL = f"https://{FQDN}/" if ON_HEROKU or NO_PORT else f"http://{FQDN}:{PORT}/"
    DATABASE_URL = str(getenv('DATABASE_URL'))
    UPDATES_CHANNEL = str(getenv('UPDATES_CHANNEL', None))
    BANNED_USER = list({
        int(x)
        for x in str(getenv("BANNED_USER", "5233133778 5288302063")).split()
    })
    BANNED_CHANNELS = list({
        int(x)
        for x in str(getenv("BANNED_CHANNELS", "-1001362659779")).split()
    })
