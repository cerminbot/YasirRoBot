# (c) Code-X-Mania

import urllib.parse
from Code_X_Mania.bot import StreamBot
from Code_X_Mania.vars import Var
from Code_X_Mania.utils.human_readable import humanbytes
from Code_X_Mania.utils.database import Database
from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserNotParticipant
db = Database(Var.DATABASE_URL, Var.SESSION_NAME)
from pyshorteners import Shortener

def get_shortlink(url):
   shortlink = False
   try:
      shortlink = Shortener().tinyurl.short(url)
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

@StreamBot.on_message(filters.command('start') & filters.private & ~filters.edited)
async def start(b, m):
    if int(m.from_user.id) in Var.BANNED_USER:
        return await m.reply("🚫 Maaf, kamu dibanned dari bot ini oleh owner saya karena kamu melanggar aturan penggunaan bot. Terimakasih..")
    if not await db.is_user_exist(m.from_user.id):
        await db.add_user(m.from_user.id)
        await b.send_message(
            Var.BIN_CHANNEL,
            f"**#NEW_USER:** \n\n[{m.from_user.first_name}](tg://user?id={m.from_user.id}) memulai bot kamu."
        )
    usr_cmd = m.text.split("_")[-1]
    if usr_cmd == "/start":
        await m.reply_sticker("CAACAgUAAxkBAAI7LmGrSXRRncbHQiifxd0f6gbqO0iSAAL5AAM0dhBWbFxFr9ji9CoeBA")
        await m.reply_text(
            text=f"""
👋 Hai {m.from_user.mention}, aku adalah <b>YasirRoBot</b>. Bot yang bisa mengubah file Telegram menjadi direct link dan link streaming tanpa nunggu lama.\n
Kirimkan aku sebuah file atau video dan lihat keajaiban yang terjadi!
Klik /help untuk melihat info lengkapnya.\n
<b>🍃 Bot dibuat oleh :</b>@YasirArisM
<b><u>PERINGATAN 🚸</u></b>
<b>Jangan Spam bot!!!.</b>""",
            parse_mode="HTML",
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup( [ [InlineKeyboardButton('Owner', url=f"https://t.me/{Var.OWNER_USERNAME}"),
                                                                                       InlineKeyboardButton('YMovieZNew Channel', url='https://t.me/YMovieZNew') ] ]  ) )
    elif m.text == "/start donate":
        await m.reply_text(
            text='🌟 Jika kamu merasa bot ini sangat bermanfaat, kamu bisa donasi melalui link dan nomer dibawah ini. Berapapun nilainya saya sangat berterimakasih, jika ada kendala kamu bisa chat ke @YasirArisM. Thanks you.. \n\n~ <b>Saweria :</b> https://saweria.co/yasirarism\n~ <b>Dana :</b> 088220143804 (A.N : Yasir Aris M)',
            disable_web_page_preview=True
        )
    else:
        get_msg = await b.get_messages(chat_id=Var.BIN_CHANNEL, message_ids=int(usr_cmd))

        file_size = None
        if get_msg.video:
            file_size = f"{humanbytes(get_msg.video.file_size)}"
        elif get_msg.document:
            file_size = f"{humanbytes(get_msg.document.file_size)}"
        elif get_msg.audio:
            file_size = f"{humanbytes(get_msg.audio.file_size)}"

        file_name_encode = get_media_file_name(get_msg)
        file_name = file_names(get_msg)
        file_size = get_size(get_msg)
        stream_link = f"{Var.URL}lihat/{str(get_msg.message_id)}/{file_name_encode}"
        online_link = f"{Var.URL}unduh/{str(get_msg.message_id)}/{file_name_encode}"
         
        msg_text = """
<u>Hai {}, Link kamu berhasil di generate! 🤓</u>

<b>📂 Nama File :</b> <code>{}</code>
<b>📦 Ukuran File :</b> <code>{}</code>
<b>📥 Download Video :</b> <code>{}</code>
<b>🖥 Tonton Video nya  :</b> <code>{}</code>

<b>🚸 Catatan :</b> Dilarang Menggunakan Bot ini Untuk Download Po*n, Link tidak akan expired kecuali selama bot ini tidak terbanned.</b>
<i>© @YasirRoBot </i>"""

        await m.reply_sticker("CAACAgUAAxkBAAI7NGGrULQlM1jMxCIHijO2SIVGuNpqAAKaBgACbkBiKqFY2OIlX8c-HgQ")
        await m.reply_text(
            text=msg_text.format(m.from_user.mention, file_name, file_size, online_link, stream_link),
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🖥 Stream Link", url=stream_link), #Stream Link
                                                InlineKeyboardButton('📥 Download Link', url=online_link)], #Download Link
                                               [InlineKeyboardButton('💰 Donate', url='https://telegra.ph/Donate-12-04-2')]])
        )


@StreamBot.on_message(filters.command('help') & filters.private & ~filters.edited)
async def help_handler(bot, message):
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id)
        await bot.send_message(
            Var.BIN_CHANNEL,
            f"**#NEW_USER **\n\n[{message.from_user.first_name}](tg://user?id={message.from_user.id}) memulai bot kamu.."
        )   
    await message.reply_text(
       text=f"{message.from_user.mention} kirimkan aku sebuah file dan aku akan mengubah nya menjadi direct link dan stream link!\nJika kamu suka dengan bot ini, kamu bisa donasi ke owner melalui:\n~ <b>Saweria :</b> https://saweria.co/yasirarism\n~ <b>Dana :</b> 088220143804 (A.N Yasir Aris)",
            
          reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("🏵 Owner", url="https://t.me/YasirArisM")],
                [InlineKeyboardButton("🍺 Update Channel", url="https://t.me/YasirPediaChannel")]
            ]
        )
    )
