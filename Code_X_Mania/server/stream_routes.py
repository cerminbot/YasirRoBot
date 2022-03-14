# (c) Code-X-Mania
import re
import time
import math
import logging
import secrets
import mimetypes
from ..vars import Var
from aiohttp import web
from aiohttp.http_exceptions import BadStatusLine
from ..bot import StreamBot
from Code_X_Mania import StartTime
from ..utils.custom_dl import TGCustomYield, chunk_size, offset_fix
from Code_X_Mania.server.exceptions import FIleNotFound, InvalidHash
from Code_X_Mania.utils.render_template import render_page
from ..utils.time_format import get_readable_time
routes = web.RouteTableDef()
from urllib.parse import quote_plus
kg18="ago"

@routes.get("/", allow_head=True)
async def root_route_handler(request):
    return web.json_response({"status": "Berjalan",
                              "maintained_by": "@YasirArisM",
                              "uptime": get_readable_time(time.time() - StartTime),
                              "Bot terakhir diupdate": get_readable_time(time.time()),
                              "ago":"",
                              "telegram_bot": '@'+(await StreamBot.get_me()).username,
                              "Bot Version":"3.0.1"})


@routes.get("/lihat/{message_id}")
@routes.get("/lihat/{message_id}/")
@routes.get(r"/lihat/{message_id:\d+}/{name}")
async def stream_handler(request):
    try:
        message_id = int(request.match_info['message_id'])
        logging.info(message_id)
        return web.Response(text=await render_page(message_id), content_type='text/html')
    except ValueError as e:
        logging.error(e)
        raise web.HTTPNotFound
        
# @routes.get("/unduh/{message_id}")
# @routes.get("/unduh/{message_id}/")
# @routes.get(r"/unduh/{message_id:\d+}/{name}")
async def old_stream_handler(request):
    try:
        message_id = int(request.match_info['message_id'])
        logging.info(message_id)
        return await media_streamer(request, message_id)
    except ValueError as e:
        logging.error(e)
        raise web.HTTPNotFound
        
@routes.get(r"/unduh/{path:\S+}", allow_head=True)
async def stream_handler(request: web.Request):
    try:
        path = request.match_info["path"]
        match = re.search(r"^([a-zA-Z0-9_-]{6})(\d+)$", path)
        if match:
            secure_hash = match.group(1)
            message_id = int(match.group(2))
        else:
            message_id = int(re.search(r"(\d+)(?:\/\S+)?", path).group(1))
            secure_hash = request.rel_url.query.get("hash")
        return await media_streamer(request, message_id, secure_hash)
    except InvalidHash as e:
        raise web.HTTPForbidden(text=e.message)
    except FIleNotFound as e:
        raise web.HTTPNotFound(text=e.message)
    except (AttributeError, BadStatusLine, ConnectionResetError):
        pass
    except Exception as e:
        logging.critical(e.with_traceback(None))
        raise web.HTTPInternalServerError(text=str(e))
        

async def media_streamer(request, message_id: int, secure_hash: str):
    range_header = request.headers.get('Range', 0)
    media_msg = await StreamBot.get_messages(Var.BIN_CHANNEL, message_id)
    file_properties = await TGCustomYield().generate_file_properties(media_msg)
    file_size = file_properties.file_size
    file_id = file_properties.file_unique_id

    if file_id.unique_id[:6] != secure_hash:
        logging.debug(f"Invalid hash for message with ID {message_id}")
        raise InvalidHash
    
    if range_header:
        from_bytes, until_bytes = range_header.replace('bytes=', '').split('-')
        from_bytes = int(from_bytes)
        until_bytes = int(until_bytes) if until_bytes else file_size - 1
    else:
        from_bytes = request.http_range.start or 0
        until_bytes = request.http_range.stop or file_size - 1

    req_length = until_bytes - from_bytes

    new_chunk_size = await chunk_size(req_length)
    offset = await offset_fix(from_bytes, new_chunk_size)
    first_part_cut = from_bytes - offset
    last_part_cut = (until_bytes % new_chunk_size) + 1
    part_count = math.ceil(req_length / new_chunk_size)
    body = TGCustomYield().yield_file(media_msg, offset, first_part_cut, last_part_cut, part_count,
                                      new_chunk_size)

    file_name = file_properties.file_name if file_properties.file_name \
        else f"{secrets.token_hex(2)}.mp4"
    mime_type = file_properties.mime_type if file_properties.mime_type \
        else f"{mimetypes.guess_type(file_name)}"

    return_resp = web.Response(
        status=206 if range_header else 200,
        body=body,
        headers={
            "Content-Type": mime_type,
            "Content-Range": f"bytes {from_bytes}-{until_bytes}/{file_size}",
            "Content-Disposition": f'attachment; filename="{file_name}"',
            "Accept-Ranges": "bytes",
        }
    )

    if return_resp.status == 200:
        return_resp.headers.add("Content-Length", str(file_size))

    return return_resp
