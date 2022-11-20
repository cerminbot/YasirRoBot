# (c) Code-x-Mania
import os
import sys
import glob
import asyncio
import logging
import importlib
from pathlib import Path
from pyrogram import idle
from .bot import StreamBot
from .vars import Var
from aiohttp import web
from .server import web_server
from .utils.keepalive import ping_server
from apscheduler.schedulers.background import BackgroundScheduler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logging.getLogger("pyrogram").setLevel(logging.WARNING)
logging.getLogger("apscheduler").setLevel(logging.WARNING)

ppath = "YasirRoBot/bot/plugins/*.py"
files = glob.glob(ppath)

loop = asyncio.get_event_loop()


async def start_services():
    print('\n')
    print('------------------- Initalizing Telegram Bot -------------------')
    await StreamBot.start()
    print('----------------------------- DONE -----------------------------')
    print('\n')
    print('--------------------------- Importing ---------------------------')
    for name in files:
        with open(name) as a:
            patt = Path(a.name)
            plugin_name = patt.stem.replace(".py", "")
            plugins_dir = Path(f"YasirRoBot/bot/plugins/{plugin_name}.py")
            import_path = f".plugins.{plugin_name}"
            spec = importlib.util.spec_from_file_location(
                import_path, plugins_dir)
            load = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(load)
            sys.modules[f"YasirRoBot.bot.plugins.{plugin_name}"] = load
            print(f"Imported => {plugin_name}")
    print(
        '-------------------- Initalizing Web Server -------------------------'
    )
    app = web.AppRunner(await web_server())
    await app.setup()
    bind_address = "0.0.0.0" if Var.ON_HEROKU else Var.BIND_ADRESS
    await web.TCPSite(app, bind_address, Var.PORT).start()
    print(
        '----------------------------- DONE ---------------------------------------------------------------------'
    )
    print('\n')
    print(
        '---------------------------------------------------------------------------------------------------------'
    )
    print(
        '---------------------------------------------------------------------------------------------------------'
    )
    print('Join https://t.me/YasirPediaChannel  to follow me for updates')
    print(
        '---------------------------------------------------------------------------------------------------------'
    )
    print('\n')
    print(
        '----------------------- Service Started -----------------------------------------------------------------'
    )
    print(
        f'                        bot =>> {(await StreamBot.get_me()).first_name}'
    )

    print(f'                        server ip =>> {bind_address}:{Var.PORT}')
    print(f'                        Owner =>> {Var.OWNER_USERNAME}')
    if Var.ON_HEROKU:
        print(f'                        app runnng on =>> {Var.FQDN}')
    print(
        '---------------------------------------------------------------------------------------------------------'
    )
    print('Give a star to my repo https://github.com/yasirarism/YasirRoBot')
    print(
        '---------------------------------------------------------------------------------------------------------'
    )
    await idle()


if __name__ == '__main__':
    try:
        loop.run_until_complete(start_services())
    except KeyboardInterrupt:
        logging.info(
            '----------------------- Service Stopped -----------------------')
