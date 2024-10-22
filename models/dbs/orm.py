import asyncio

from models.databases import Session
from models.dbs.models import *

from sqlalchemy import insert, inspect, or_, select, text, update


class Orm:
    
    @staticmethod
    async def update_birth_date(telegram_id, date):
        async with Session() as session:
            query = (
                update(User)
                .where(User.telegram_id == telegram_id)
                .values(birth_date=date)
            )
            await session.execute(query)
            await session.commit()
    
    @classmethod
    async def create_user(cls, message):
        if await cls.get_user_by_telegram_id(message.from_user.id) is None:
            user = User(
                full_name=message.from_user.full_name,
                telegram_id=message.from_user.id,
                username=message.from_user.username
            )
            await cls.save_user(user)
    
    @staticmethod
    async def save_user(user):
        async with Session() as session:
            await session.merge(user)
            await session.commit()
    
    @staticmethod
    async def get_user_by_telegram_id(telegram_id):
        async with Session() as session:
            query = select(User).where(User.telegram_id == telegram_id)
            user = (await session.execute(query)).scalar_one_or_none()
            return user
    
    @staticmethod
    async def get_all_users():
        async with Session() as session:
            query = select(User)
            users = (await session.execute(query)).scalars().all()
            return users
        