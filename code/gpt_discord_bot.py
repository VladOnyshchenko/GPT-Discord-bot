# -*- coding: utf-8 -*-
import discord  # Импортируем модуль discord, который позволяет взаимодействовать с Discord API
import openai  # Импортируем модуль openai, который используется для работы с OpenAI API
import configparser  # Импортируем модуль configparser для работы с конфигурационными файлами

config = configparser.ConfigParser()  # Создаем объект configparser
config.read('config.ini')  # Читаем конфигурационный файл

openai.api_key = config['DEFAULT']['OpenAI_API_Key']
token = config['DEFAULT']['Discord_Token']
CHANNEL_ID = int(config['DEFAULT']['Channel_ID'])
Vlad_ID = int(config['DEFAULT']['Vlad_ID'])
Voron_ID = int(config['DEFAULT']['Voron_ID'])

# Создаем объект intents с настройками для клиента Discord
intents = discord.Intents.default()
intents.message_content = True

# Создаем клиент Discord
client = discord.Client(intents=intents)

# Создаем список для хранения сообщений пользователя и бота
user_context = []
bot_context = []


# Функция для генерации ответа
async def generate_response(message):
    # Добавляем сообщение пользователя в список контекста
    user_context.append(message)
    # Если количество сообщений в списке контекста превышает 3, удаляем самое старое сообщение
    if len(user_context) > 3:
        user_context.pop(0)

    # Создаем список сообщений для передачи в модель OpenAI
    messages = [{"role": "system", "content": "User messages:"}]
    for msg in user_context:
        messages.append({"role": "user", "content": msg})

    # Если есть сообщения от бота, добавляем их в список сообщений
    if len(bot_context) > 0:
        messages.append({"role": "system", "content": "Bot messages:"})
        for msg in bot_context:
            messages.append({"role": "assistant", "content": msg})

            # Добавляем специальный комментарий, чтобы бот понимал, где начинается сообщение пользователя
            messages.append({"role": "system", "content": "<USER_MESSAGE_STARTS_HERE>"})

    # Генерируем ответ с помощью модели OpenAI ChatCompletion
    completions = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
    )
    # Получаем последнее сообщение из ответа и его содержимое
    response = completions.choices[-1].message
    response_content = response['content']

    # Добавляем ответ бота в список контекста
    bot_context.append(response_content)
    # Если количество ответов в списке контекста превышает 3, удаляем самый старый ответ
    if len(bot_context) > 3:
        bot_context.pop(0)

    # Возвращаем содержимое ответа
    return response_content


# Функция для отправки ответа в указанный канал
async def send_response(channel, content):
    # Если содержимое ответа слишком большое, разделяем его на части и отправляем по частям
    if len(content) > 1999:
        chunks = [content[i:i + 1999] for i in range(0, len(content), 1999)]
        for chunk in chunks:
            await channel.send(chunk)
    else:
        await channel.send(content)


# Функция, вызываемая при успешном подключении клиента к Discord
@client.event
async def on_ready():
    print(f'{client.user.name} has connected to Discord!')


# Функция, вызываемая при получении нового сообщения
@client.event
async def on_message(message):
    # Если автор сообщения - бот, игнорируем его
    if message.author == client.user:
        return

    # Если сообщение от пользователя с ID Vlad_ID или Voron_ID или находится на нужном канале, обрабатываем его
    if (isinstance(message.channel, discord.DMChannel) and message.author.id in [Vlad_ID, Voron_ID]) or message.channel.id == CHANNEL_ID:
        if len(message.content.strip()) > 0:
            # Генерируем ответ на основе содержимого сообщения пользователя
            response_content = await generate_response(message.content)
            # Отправляем ответ в канал, откуда пришло сообщение
            await send_response(message.channel, response_content)


# Запускаем клиент Discord
client.run(token)
