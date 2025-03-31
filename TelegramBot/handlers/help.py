from aiogram import Bot
from aiogram.types import Message


async def cmd_help(message: Message, bot: Bot):
    await message.answer("Dotabuffer Bot предназначен для легкого поиска актуалной информации о персонажах, предметах и сборках. Чтобы использовать бота необходимо написать команду '/start'")