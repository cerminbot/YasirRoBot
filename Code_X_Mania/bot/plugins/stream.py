# (c) Code-X-Mania

import requests
import asyncio
from Code_X_Mania.bot import StreamBot
from Code_X_Mania.utils.database import Database
from Code_X_Mania.utils.human_readable import humanbytes
from Code_X_Mania.vars import Var
from pyrogram import filters, Client
from pyrogram.errors import FloodWait, UserNotParticipant, ChatAdminRequired
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
db = Database(Var.DATABASE_URL, Var.SESSION_NAME)
from pyshorteners import Shortener



def get_shortlink(url):
   shortlink = False 
   try:
      shortlink = Shortener().dagd.short(url)
   except Exception as err:
       print(err)
       pass
   return shortlink

@StreamBot.on_message(filters.private & (filters.document | filters.video | filters.audio) & ~filters.edited, group=4)
async def private_receive_handler(c: Client, m: Message):
    if not await db.is_user_exist(m.from_user.id):
        await db.add_user(m.from_user.id)
        await c.send_message(
            Var.BIN_CHANNEL,
            f"#NEW_USER : \n\nPengguna baru [{m.from_user.first_name}](tg://user?id={m.from_user.id}) menggunakan bot kamu !!"
        )
    try:
        log_msg = await m.forward(chat_id=Var.BIN_CHANNEL)
        stream_link = Var.URL + 'lihat/' + str(log_msg.message_id)
        #shortlink = get_shortlink(stream_link) 
        #if shortlink:
            #stream_link = shortlink
        online_link = Var.URL + 'unduh/'+ str(log_msg.message_id) 
        #shortlinka = get_shortlink(online_link)
        #if shortlinka:
            #online_link = shortlinka
        
        file_size = None
        if m.video:
            file_size = f"{humanbytes(m.video.file_size)}"
        elif m.document:
            file_size = f"{humanbytes(m.document.file_size)}"
        elif m.audio:
            file_size = f"{humanbytes(m.audio.file_size)}"

        file_name = None
        if m.video:
            file_name = f"{m.video.file_name}"
        elif m.document:
            file_name = f"{m.document.file_name}"
        elif m.audio:
            file_name = f"{m.audio.file_name}"

        msg_text ="""
<i><u>Hai {}, Link mu sudah digenerate! 🤓</u></i>

<b>📂 Nama File :</b> <code>{}</code>
<b>📦 Ukuran File :</b> <code>{}</code>

<b>CATATAN : Link tidak akan expired kecuali ada yang menyalahgunakan bot ini.</b>
© @YasirRoBot"""

        await log_msg.reply_text(text=f"**Di Minta Oleh :** [{m.from_user.first_name}](tg://user?id={m.from_user.id})\n**ID User :** `{m.from_user.id}`\n**Download Link :** {stream_link}", disable_web_page_preview=True, parse_mode="Markdown", quote=True)
        await m.reply_sticker("CAACAgUAAxkBAAI7NGGrULQlM1jMxCIHijO2SIVGuNpqAAKaBgACbkBiKqFY2OIlX8c-HgQ")
        await m.reply_text(
            text=msg_text.format(m.from_user.mention, file_name, file_size),
            parse_mode="HTML", 
            quote=True,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🖥 Streaming Link", url=stream_link), #Stream Link
                                                InlineKeyboardButton('📥 Download Link', url=online_link)], #Download Link
                                              [InlineKeyboardButton('💰 Donate', url='https://telegra.ph/Donate-12-04-2')]])
        )
    except FloodWait as e:
        print(f"Sleeping for {str(e.x)}s")
        await asyncio.sleep(e.x)
        await c.send_message(chat_id=Var.BIN_CHANNEL, text=f"Dapat floodwait {str(e.x)}s dari [{m.from_user.first_name}](tg://user?id={m.from_user.id})\n\n**𝚄𝚜𝚎𝚛 𝙸𝙳 :** `{str(m.from_user.id)}`", disable_web_page_preview=True, parse_mode="Markdown")


@StreamBot.on_message(filters.channel & (filters.document | filters.video) & ~filters.edited, ~filters.chat(-1001279146310), group=-1)
async def channel_receive_handler(bot, broadcast):
    if int(broadcast.chat.id) in Var.BANNED_CHANNELS:
        await bot.leave_chat(broadcast.chat.id)
        return
    try:
        try:
           log_msg = await broadcast.forward(chat_id=Var.BIN_CHANNEL)
        except Exception:
           log_msg = await broadcast.copy(chat_id=Var.BIN_CHANNEL)
        stream_link = Var.URL + 'lihat/' + str(log_msg.message_id) 
        online_link = Var.URL + 'unduh/' + str(log_msg.message_id)
        await log_msg.reply_text(
            text=f"**Nama Channel:** `{broadcast.chat.title}`\n**ID Channel:** `{broadcast.chat.id}`\n**URL Request:** {stream_link}",
            quote=True,
            parse_mode="Markdown"
        )
        await bot.edit_message_reply_markup(
            chat_id=broadcast.chat.id,
            message_id=broadcast.message_id,
            reply_markup=InlineKeyboardMarkup(
                [
                   [InlineKeyboardButton('📥 Stream & Download Link', url=f"https://t.me/{(await bot.get_me()).username}?start=YasirBot_{str(log_msg.message_id)}")]
                ]
            )
        )
    except ChatAdminRequired:
        await bot.leave_chat(broadcast.chat.id)
    except FloodWait as w:
        print(f"Sleeping for {str(w.x)}s")
        await asyncio.sleep(w.x)
        await bot.send_message(chat_id=Var.BIN_CHANNEL,
                             text=f"Mendapat floodwait {str(w.x)} detik dari {broadcast.chat.title}\n\n**ID Channel:** `{str(broadcast.chat.id)}`",
                             disable_web_page_preview=True, parse_mode="Markdown")
    except Exception as e:
        await bot.send_message(chat_id=Var.BIN_CHANNEL, text=f"**#ERROR_TRACEBACK:** `{e}`", disable_web_page_preview=True, parse_mode="Markdown")
        print(f"Tidak bisa edit pesan broadcast!\ERROR:  **Beri aku ijin edit pesan di channel{e}**")
