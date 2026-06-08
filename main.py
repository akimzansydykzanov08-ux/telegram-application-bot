import aiogram
import asyncio
from aiogram import Bot, Dispatcher
from config import TOKEN
from handlers import router
from database import init_db
from aiogram.client.default import DefaultBotProperties 
from aiogram.enums import ParseMode

dp = Dispatcher()
bot = Bot(token=TOKEN, default_properties=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))
dp.include_router(router)

async def main():
    init_db()
    print("---bot is running---")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())



