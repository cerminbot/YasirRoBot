# (c) Code-X-Mania

import datetime
import motor.motor_asyncio


class Database:

    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.col = self.db.users
        self.ban = self.db.banned_users

    def new_user(self, id):
        return dict(id=id, join_date=datetime.date.today().isoformat())

    async def add_ban_user(self, id):
        await self.ban.insert_one({'id': int(id)})

    async def is_banned(self, id):
        user = await self.ban.find_one({'id': int(id)})
        return bool(user)

    async def remove_ban(self, user_id):
        await self.ban.delete_many({'id': int(user_id)})

    async def add_user(self, id):
        user = self.new_user(id)
        await self.col.insert_one(user)

    async def is_user_exist(self, id):
        user = await self.col.find_one({'id': int(id)})
        return bool(user)

    async def total_users_count(self):
        count = await self.col.count_documents({})
        return count

    async def get_all_users(self):
        return self.col.find({})

    async def delete_user(self, user_id):
        await self.col.delete_many({'id': int(user_id)})
