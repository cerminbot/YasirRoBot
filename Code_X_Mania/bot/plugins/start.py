# (c) Code-X-Mania

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
       pass
   return shortlink

@StreamBot.on_message(filters.command('start') & filters.private & ~filters.edited)
async def start(b, m):
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
            text="""
👋 Hai, aku adalah <b>YasirRoBot</b>. Bot yang bisa mengubah file Telegram menjadi direct link dan link streaming tanpa nunggu lama.\n
Kirimkan aku sebuah file atau video dan lihat keajaiban yang terjadi!
Klik /help untuk melihat info lengkapnya.\n
<b>🍃 Bot dibuat oleh :</b>@YasirArisM
<b><u>PERINGATAN 🚸</u></b>
<b>Jangan Spam bot!!!.</b>""",
            parse_mode="HTML",
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup( [ [InlineKeyboardButton('Owner', url=f"https://t.me/{Var.OWNER_USERNAME}"),
                                                                                       InlineKeyboardButton('Gabung Channel ', url='https://t.me/YasirPediaChannel') ] ]  ) )
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

        file_name = None
        if get_msg.video:
            file_name = f"{get_msg.video.file_name}"
        elif get_msg.document:
            file_name = f"{get_msg.document.file_name}"
        elif get_msg.audio:
            file_name = f"{get_msg.audio.file_name}"

        stream_link = Var.URL + 'tonton/' + str(get_msg.message_id)
        #shortlink = get_shortlink(stream_link)
        #if shortlink:
            #stream_link = shortlink
        online_link = Var.URL + 'unduh/' + str(get_msg.message_id)
        #shortlinka = get_shortlink(online_link)
        #if shortlinka:
            #online_link = shortlinka

        msg_text ="""
<u>Yeaaayyyy! 😁, Link kamu berhasil di generate! 🤓</u>
<b>📂 Nama File :</b> <code>{}</code>
<b>📦 Ukuran File :</b> <code>{}</code>
<b>📥 Download Video :</b> <code>{}</code>
<b>🖥 Tonton Video nya  :</b> <code>{}</code>
<b>🚸 Catatan :</b> Link tidak akan expired, kecuali saya yang hapus jika kamu menyalahgunakan bot ini.
<i>© @YasirRoBot </i>"""

        await m.reply_sticker("CAACAgUAAxkBAAI7NGGrULQlM1jMxCIHijO2SIVGuNpqAAKaBgACbkBiKqFY2OIlX8c-HgQ")
        await m.reply_text(
            text=msg_text.format(file_name, file_size, online_link, stream_link),
            parse_mode="HTML",
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
       text="Kirimkan aku sebuah file dan aku akan mengubah nya menjadi direct link dan stream link!\nJika kamu suka dengan bot ini, kamu bisa donasi ke owner melalui:\n~ <b>Saweria :</b> https://saweria.co/yasirarism\n~ <b>Dana :</b> 088220143804 (A.N Yasir Aris)",
            parse_mode="HTML",
            
          reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("🏵 Owner", url="https://t.me/YasirArisM")],
                [InlineKeyboardButton("🍺 Update Channel", url="https://t.me/YasirPediaChannel")]
            ]
        )
    )
