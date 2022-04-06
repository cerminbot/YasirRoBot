# (c) Code-X-Mania
import re
import time
import math
import logging
import secrets
import mimetypes
from ..vars import Var
from bs4 import BeautifulSoup
from aiohttp import web, ClientSession
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

async def getcontent(url):
    headers = {   
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '   
        'Chrome/61.0.3163.100 Safari/537.36'   
    }
    async with ClientSession(headers=headers) as session:  
        r = await session.get(url)  
        return await r.read() 

@routes.get("/", allow_head=True)
async def root_route_handler(request):
    return web.json_response({"status": "Berjalan",
                              "maintained_by": "@YasirArisM",
                              "uptime": get_readable_time(time.time() - StartTime),
                              "Bot terakhir diupdate": get_readable_time(time.time()),
                              "ago":"",
                              "telegram_bot": '@'+(await StreamBot.get_me()).username,
                              "Bot Version":"3.0.1"})

@routes.get("/google?query={query}")
async def google_api(request):
      query = request.match_info['query']
      headers = {   
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '   
        'Chrome/61.0.3163.100 Safari/537.36'   
       }
       html = await getcontent(f'https://www.google.com/search?q={query}')
       soup = BeautifulSoup(html.text, 'lxml')

       # collect data
       data = []

       for result in soup.select('.tF2Cxc'):
          title = result.select_one('.DKV0Md').text
          link = result.select_one('.yuRUbf a')['href']
          try:
            snippet = result.select_one('#rso .lyLwlc').text
          except:
            snippet = "-"

          # appending data to an array
          data.append({
            'title': title,
            'link': link,
            'snippet': snippet,
          })
       return web.json_response(data)

@routes.get("/lk21/{judul}")
async def lk21_api(request):
       title = request.match_info['judul']
       headers = {
           'User-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.19582"
       }

       html = await getcontent(f"https://149.56.24.226/?s={title}")
       soup = BeautifulSoup(html, 'lxml')
       data = []
       for res in soup.find_all(class_='search-item'):
          link = res.select('a')[0]['href']
          judul = res.select('a')[1]['title']
          try:
             r1 = res.select('a')[2].text
          except:
             r1 = ''
          try:
             r2 = res.select('a')[3].text
          except:
             r2 = ''
          try:
             r3 = res.select('a')[4].text
          except:
             r3 = ''
          try:
             r4 = res.select('a')[5].text
          except:
             r4 = ''
          try:
             r5 = res.select('a')[6].text
          except:
             r5 = ''
          ddl = link.split("/")[3]
          dl = f"https://asdahsdkjajslkfbkaujsgfbjaeghfyjj76e8637e68723rhbfajkl.rodanesia.com/get/{ddl}"
          data.append({
              'judul': judul,
              'link': link,
              'kualitas': f'{r1} {r2} {r3} {r4} {r5}',
              'dl': dl
          })
       return web.json_response(data)

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
        
        
@routes.get("/unduh/{message_id}")
@routes.get("/unduh/{message_id}/")
@routes.get(r"/unduh/{message_id:\d+}/{name}")
async def stream_handler(request):
    try:
        message_id = int(request.match_info['message_id'])
        return await media_streamer(request, message_id)
    except InvalidHash as e:
        raise web.HTTPForbidden(text=e.message)
    except FIleNotFound as e:
        raise web.HTTPNotFound(text=e.message)
    except (AttributeError, BadStatusLine, ConnectionResetError):
        pass
    except Exception as e:
        logging.critical(e.with_traceback(None))
        raise web.HTTPInternalServerError(text=str(e))
        

async def media_streamer(request, message_id: int):
    range_header = request.headers.get('Range', 0)
    media_msg = await StreamBot.get_messages(Var.BIN_CHANNEL, message_id)
    file_properties = await TGCustomYield().generate_file_properties(media_msg)
    file_size = file_properties.file_size

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

    file_name = file_properties.file_name or f"{secrets.token_hex(2)}.mp4"
    mime_type = file_properties.mime_type or f"{mimetypes.guess_type(file_name)}"

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
