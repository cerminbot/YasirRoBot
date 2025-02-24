# (c) Code-x-Mania
from YasirRoBot.vars import Var
from YasirRoBot.bot import StreamBot
from YasirRoBot.utils.custom_dl import TGCustomYield
from YasirRoBot.utils.file_size import human_size
import urllib.parse
import secrets
import mimetypes
import aiofiles
import logging
import aiohttp


async def fetch_properties(message_id):
    media_msg = await StreamBot.get_messages(Var.BIN_CHANNEL, message_id)
    file_properties = await TGCustomYield().generate_file_properties(media_msg)
    file_name = file_properties.file_name or f"{secrets.token_hex(2)}.jpeg"
    mime_type = file_properties.mime_type or f"{mimetypes.guess_type(file_name)}"
    return file_name, mime_type


async def render_page(message_id):
    file_name, mime_type = await fetch_properties(message_id)
    src = urllib.parse.urljoin(Var.URL, str(message_id))
    audio_formats = [
        'audio/mpeg', 'audio/mp4', 'audio/x-mpegurl', 'audio/vnd.wav'
    ]
    video_formats = [
        'video/mp4', 'video/avi', 'video/ogg', 'video/h264', 'video/h265',
        'video/x-matroska'
    ]
    if mime_type.lower() in video_formats:
        async with aiofiles.open('YasirRoBot/template/req.html') as r:
            heading = f'Watch {file_name}'
            tag = mime_type.split('/')[0].strip()
            html = (await r.read()).replace('tag',
                                            tag) % (heading, file_name, src)
    elif mime_type.lower() in audio_formats:
        async with aiofiles.open('YasirRoBot/template/req.html') as r:
            heading = f'Listen {file_name}'
            tag = mime_type.split('/')[0].strip()
            html = (await r.read()).replace('tag',
                                            tag) % (heading, file_name, src)
    else:
        async with aiofiles.open('YasirRoBot/template/dl.html') as r:
            async with aiohttp.ClientSession() as s:
                async with s.get(src) as u:
                    file_size = human_size(u.headers.get('Content-Type'))
                    html = (await
                            r.read()) % (heading, file_name, src, file_size)
    return html
