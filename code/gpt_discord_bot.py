# -*- coding: utf-8 -*-
import discord
from discord.ext import commands
from openai import OpenAI
import configparser

# Читаем конфигурационный файл
config = configparser.ConfigParser()
config.read('config.ini')

# Извлекаем параметры
api_key = config['DEFAULT']['OpenAI_API_Key']
token = config['DEFAULT']['Discord_Token']
CHANNEL_ID = int(config['DEFAULT']['Channel_ID'])
VLAD_ID = int(config['DEFAULT']['Vlad_ID'])
VORON_ID = int(config['DEFAULT']['Voron_ID'])  # Добавляем второго пользователя

# Инициализируем клиент OpenAI
client_openai = OpenAI(api_key=api_key)

# Настраиваем intents для Discord
intents = discord.Intents.default()
intents.message_content = True
intents.messages = True

# Инициализируем бота
bot = commands.Bot(command_prefix='!', intents=intents)

# Словарь для хранения тредов пользователей
user_threads = {}

# Функция генерации ответа от OpenAI
async def generate_response(message_content, user_id):
    user_thread = user_threads.setdefault(user_id, [])
    user_thread.append({"role": "user", "content": message_content})

    try:
        response = client_openai.chat.completions.create(
            model="gpt-3.5-turbo",  # Актуальная модель (можно заменить на gpt-3.5-turbo)
            messages=user_thread,
            max_tokens=4096
        )

        if response.choices and response.choices[0].message.content:
            assistant_response = response.choices[0].message.content
            user_thread.append({"role": "assistant", "content": assistant_response})

            # Ограничение по токенам
            total_tokens = sum(len(msg["content"].split()) for msg in user_thread)
            while total_tokens > 4096:
                user_thread.pop(0)
                total_tokens = sum(len(msg["content"].split()) for msg in user_thread)

            return assistant_response
        else:
            return "Ошибка: пустой ответ от OpenAI."
    except Exception as e:
        print(f"Ошибка OpenAI: {e}")
        return "Произошла ошибка при генерации ответа."

# Функция отправки ответа
async def send_response(channel, content):
    if len(content) > 2000:  # Лимит Discord — 2000 символов
        chunks = [content[i:i + 2000] for i in range(0, len(content), 2000)]
        for chunk in chunks:
            await channel.send(chunk)
    else:
        await channel.send(content)

# Событие: бот готов
@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

# Событие: обработка сообщений
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # Поддержка двух пользователей в ЛС и указанного канала
    if (isinstance(message.channel, discord.DMChannel) and message.author.id in [VLAD_ID, VORON_ID]) or message.channel.id == CHANNEL_ID:
        if message.content.strip():
            response_content = await generate_response(message.content, message.author.id)
            await send_response(message.channel, response_content)

# Запуск бота
bot.run(token)