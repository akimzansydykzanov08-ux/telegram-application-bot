import aiogram
import asyncio
from aiogram import Bot, Dispatcher
from config import TOKEN
from handlers import router
from database import init_db

dp = Dispatcher()
bot = Bot(TOKEN)
dp.include_router(router)

async def main():
    init_db()
    print("---bot is running---")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())



