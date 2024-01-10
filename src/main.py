import asyncio
import logging
import sys

from aiogram import Dispatcher
from aiogram.fsm.strategy import FSMStrategy
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncEngine

from examobot.bot import ExamOBot
from examobot.db.manager import DBManager
from examobot.db.tables import *
from examobot.definitions import DEFAULT_DB_FILE, TOKEN
from examobot.definitions import MAIN_LOG_FILE, LOG_IN_FILE


class EngineManager:
    def __init__(self, path: str) -> None:
        self.path = path

    async def __aenter__(self) -> AsyncEngine:
        self.engine = create_async_engine(self.path, echo=True)
        return self.engine

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.engine.dispose()


async def main() -> None:
    dp = Dispatcher(fsm_strategy=FSMStrategy.USER_IN_TOPIC)
    with open(MAIN_LOG_FILE, "a") as log:
        if LOG_IN_FILE:
            logging.basicConfig(level=logging.INFO, stream=log)
        else:
            logging.basicConfig(level=logging.INFO, stream=sys.stdout)

        async with EngineManager('sqlite+aiosqlite:///' + DEFAULT_DB_FILE) as engine:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)

            async_session_maker = async_sessionmaker(engine, expire_on_commit=False)
            db_manager = DBManager(async_session_maker)
            # await db_manager.initial_add()

            bot = ExamOBot(TOKEN, dp, db_manager)
            await bot.run()


if __name__ == '__main__':
    asyncio.run(main())
