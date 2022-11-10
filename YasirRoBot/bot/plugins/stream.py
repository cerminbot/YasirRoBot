# (c) Code-X-Mania

import requests
import urllib.parse
import asyncio
from YasirRoBot.bot import StreamBot
from YasirRoBot.utils.database import Database
from YasirRoBot.utils.human_readable import humanbytes
from YasirRoBot.utils import cooldown_helper
from YasirRoBot.vars import Var
from pyrogram import filters, Client
from pyrogram.errors import FloodWait, UserNotParticipant, ChatAdminRequired
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

db = Database(Var.DATABASE_URL, Var.SESSION_NAME)
from pyshorteners import Shortener
from YasirRoBot.utils.file_properties import get_hash, get_name


def get_shortlink(url):
    shortlink = False
    try:
        shortlink = Shortener().dagd.short(url)
    except Exception as err:
        print(err)
    return shortlink


def get_media_file_name(m):
    media = m.video or m.document or m.audio
    if media and media.file_name:
        return urllib.parse.quote_plus(media.file_name)
    else:
        return media.file_unique_id


def file_names(m):
    media = m.video or m.document or m.audio
    return media.file_name if media and media.file_name else media.file_unique_id


def get_size(m):
    file_size = None
    if m.video:
        file_size = f"{humanbytes(m.video.file_size)}"
    elif m.document:
        file_size = f"{humanbytes(m.document.file_size)}"
    elif m.audio:
        file_size = f"{humanbytes(m.audio.file_size)}"
    return file_size


@StreamBot.on_message(filters.private &
                      (filters.document | filters.video | filters.audio),
                      group=4)
async def private_receive_handler(c: Client, m: Message):
    if await db.is_banned(int(m.from_user.id)):
        return await m.reply(
            "🚫 Maaf, kamu dibanned dari bot ini oleh owner saya karena kamu melanggar aturan penggunaan bot. Terimakasih..\n\n🚫 Sorry, you have been banned from this bot because you have violated the user rules. Thank you.."
        )
    if not await db.is_user_exist(m.from_user.id):
        await db.add_user(m.from_user.id)
        await c.send_message(
            Var.BIN_CHANNEL,
            f"#NEW_USER : \n\nPengguna baru [{m.from_user.first_name}](tg://user?id={m.from_user.id}) menggunakan bot kamu !!"
        )
    try:
        log_msg = await m.forward(chat_id=Var.BIN_CHANNEL)
        file_name_encode = get_media_file_name(log_msg)
        file_name = file_names(log_msg)
        file_size = get_size(log_msg)
        stream_link = f"{Var.URL}lihat/{str(log_msg.id)}/{file_name_encode}"
        online_link = f"{Var.URL}unduh/{str(log_msg.id)}/{file_name_encode}"
        # stream_link = f"{Var.URL}lihat/{str(log_msg.message_id)}/{file_name_encode}"
        # online_link = f"{Var.URL}unduh/{str(log_msg.message_id)}/{file_name_encode}"

        msg_text = """
<i><u>Hai {}, Link mu sudah digenerate! 🤓</u></i>

<b>📂 Nama File :</b> <code>{}</code>
<b>📦 Ukuran File :</b> <code>{}</code>
<b>📥 Download Video :</b> <code>{}</code>
<b>🖥 Tonton Video nya  :</b> <code>{}</code>

<b>CATATAN : Dilarang menggunakan bot ini untuk download Po*n, Link tidak akan expired kecuali ada yang menyalahgunakan bot ini.</b>
© @YasirRoBot"""

        await log_msg.reply_text(
            text=
            f"**Di Minta Oleh :** [{m.from_user.first_name}](tg://user?id={m.from_user.id})\n**ID User :** `{m.from_user.id}`\n**Download Link :** {stream_link}",
            disable_web_page_preview=True,
            quote=True)
        await m.reply_sticker(
            "CAACAgUAAxkBAAI7NGGrULQlM1jMxCIHijO2SIVGuNpqAAKaBgACbkBiKqFY2OIlX8c-HgQ"
        )
        await m.reply_text(
            text=msg_text.format(m.from_user.mention, file_name, file_size,
                                 online_link, stream_link),
            quote=True,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("🖥 Streaming Link",
                                         url=stream_link),  #Stream Link
                    InlineKeyboardButton('📥 Download Link', url=online_link)
                ],  #Download Link
                [
                    InlineKeyboardButton(
                        '💰 Donate', url='https://telegra.ph/Donate-12-04-2')
                ]
            ]))
    except FloodWait as e:
        print(f"Sleeping for {str(e.value)}s")
        await asyncio.sleep(e.value)
        await c.send_message(
            chat_id=Var.BIN_CHANNEL,
            text=
            f"Dapat floodwait {str(e.value)}s dari [{m.from_user.first_name}](tg://user?id={m.from_user.id})\n\n**𝚄𝚜𝚎𝚛 𝙸𝙳 :** `{str(m.from_user.id)}`",
            disable_web_page_preview=True,
            parse_mode="Markdown")


@StreamBot.on_message(filters.channel & (filters.document | filters.video),
                      group=-1)
async def channel_receive_handler(bot, broadcast):
    if broadcast.chat.id == -1001623503648:
        return
    elif int(broadcast.chat.id) in Var.BANNED_CHANNELS:
        await bot.leave_chat(broadcast.chat.id)
        return
    try:
        try:
            log_msg = await broadcast.forward(chat_id=Var.BIN_CHANNEL)
        except Exception:
            log_msg = await broadcast.copy(chat_id=Var.BIN_CHANNEL)
        stream_link = f'{Var.URL}lihat/{str(log_msg.id)}'
        online_link = f'{Var.URL}unduh/{str(log_msg.id)}'
        await log_msg.reply_text(
            text=
            f"**Nama Channel:** `{broadcast.chat.title}`\n**ID Channel:** `{broadcast.chat.id}`\n**URL Request:** {stream_link}",
            quote=True,
        )
        await bot.edit_message_reply_markup(
            chat_id=broadcast.chat.id,
            message_id=broadcast.id,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton(
                    '📥 Stream & Download Link',
                    url=
                    f"https://t.me/{(await bot.get_me()).username}?start=YasirBot_{str(log_msg.id)}"
                )
            ]]))
    except ChatAdminRequired:
        await bot.leave_chat(broadcast.chat.id)
    except FloodWait as w:
        print(f"Sleeping for {str(w.value)}s")
        await asyncio.sleep(w.value)
        await bot.send_message(
            chat_id=Var.BIN_CHANNEL,
            text=
            f"Mendapat floodwait {str(w.value)} detik dari {broadcast.chat.title}\n\n**ID Channel:** `{str(broadcast.chat.id)}`",
            disable_web_page_preview=True)
    except Exception as e:
        await bot.send_message(chat_id=Var.BIN_CHANNEL,
                               text=f"**#ERROR_TRACEBACK:** `{e}`",
                               disable_web_page_preview=True)
        print(
            f"Tidak bisa edit pesan broadcast!\ERROR:  **Beri aku ijin edit pesan di channel{e}**"
        )
