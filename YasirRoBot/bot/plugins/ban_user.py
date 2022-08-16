from YasirRoBot.bot import StreamBot
from YasirRoBot.vars import Var
from pyrogram import filters
from YasirRoBot.utils.database import Database

db = Database(Var.DATABASE_URL, Var.SESSION_NAME)


@StreamBot.on_message(
    filters.command('ban') & filters.private & filters.user(Var.OWNER_ID))
async def ban_handler(bot, m):
    if len(m.command) == 1:
        await m.reply_text(
            text="🚫 Gunakan: /ban [id user] untuk membanned pengguna.")
        return
    user = m.command[1]
    if not await db.is_banned(user):
        await db.add_ban_user(user)
        await m.reply(f"🚫 User {user} berhasil dibanned dari bot ini.")
    else:
        await m.reply(f"🚫 User {user} sudah dibanned sebelumnya.")


@StreamBot.on_message(
    filters.command('remove_ban') & filters.private
    & filters.user(Var.OWNER_ID))
async def rm_ban_handler(bot, m):
    if len(m.command) == 1:
        await m.reply_text(
            text="🚫 Gunakan: /remove_ban [id user] untuk unban pengguna.")
        return
    user = m.command[1]
    await db.remove_ban(user)
    await m.reply(f"🚫 User {user} berhasil diunbanned dari bot ini.")