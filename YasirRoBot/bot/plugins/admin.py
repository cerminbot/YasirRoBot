# (c) @code-x-mania
import os
import time
import string
import random
import asyncio
import aiofiles
import datetime
from YasirRoBot.utils.broadcast_helper import send_msg
from YasirRoBot.utils.database import Database
from YasirRoBot.bot import StreamBot
from YasirRoBot.vars import Var
from pyrogram import filters, Client
from pyrogram.types import Message

db = Database(Var.DATABASE_URL, Var.SESSION_NAME)
broadcast_ids = {}


@StreamBot.on_message(
    filters.command("status") & filters.private & filters.user(Var.OWNER_ID))
async def sts(c: Client, m: Message):
    total_users = await db.total_users_count()
    await m.reply_text(text=f"**Numbers of users:** `{total_users}`")


@StreamBot.on_message(
    filters.command("broadcast") & filters.private
    & filters.user(Var.OWNER_ID))
async def broadcast_(c, m):
    user_id = m.from_user.id
    out = await m.reply_text(
        text=
        "Broadcast initiated! You will be notified with log file when all the users are notified."
    )

    all_users = await db.get_all_users()
    broadcast_msg = m.reply_to_message
    while True:
        broadcast_id = ''.join(
            [random.choice(string.ascii_letters) for _ in range(3)])
        if not broadcast_ids.get(broadcast_id):
            break
    start_time = time.time()
    total_users = await db.total_users_count()
    done = 0
    failed = 0
    success = 0
    broadcast_ids[broadcast_id] = dict(total=total_users,
                                       current=done,
                                       failed=failed,
                                       success=success)
    async with aiofiles.open('broadcast.txt', 'w') as broadcast_log_file:
        async for user in all_users:
            sts, msg = await send_msg(user_id=int(user['id']),
                                      message=broadcast_msg)
            if msg is not None:
                await broadcast_log_file.write(msg)
            if sts == 200:
                success += 1
            else:
                failed += 1
            if sts == 400:
                await db.delete_user(user['id'])
            done += 1
            if broadcast_ids.get(broadcast_id) is None:
                break
            else:
                broadcast_ids[broadcast_id].update(
                    dict(current=done, failed=failed, success=success))
    if broadcast_ids.get(broadcast_id):
        broadcast_ids.pop(broadcast_id)
    completed_in = datetime.timedelta(seconds=int(time.time() - start_time))
    await asyncio.sleep(3)
    await out.delete()
    if failed == 0:
        await m.reply_text(
            text=
            f"broadcast completed in `{completed_in}`\n\nTotal users {total_users}.\nTotal done {done}, {success} success and {failed} failed.",
            quote=True)
    else:
        await m.reply_document(
            document='broadcast.txt',
            caption=
            f"broadcast completed in `{completed_in}`\n\nTotal users {total_users}.\nTotal done {done}, {success} success and {failed} failed.",
            quote=True)
    os.remove('broadcast.txt')
