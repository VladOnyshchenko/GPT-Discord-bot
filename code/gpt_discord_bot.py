# -*- coding: utf-8 -*-
from openai import OpenAI
import discord
import configparser

# Создаем объект configparser для чтения конфигурационного файла
config = configparser.ConfigParser()
config.read('config.ini')

# Извлекаем ключи из конфигурационного файла
api_key = config['DEFAULT']['OpenAI_API_Key']
token = config['DEFAULT']['Discord_Token']
CHANNEL_ID = int(config['DEFAULT']['Channel_ID'])
Vlad_ID = int(config['DEFAULT']['Vlad_ID'])

# Создаем объект OpenAI
client = OpenAI(api_key=api_key)

# Создаем объект intents с настройками для клиента Discord
intents = discord.Intents.default()
intents.message_content = True

# Создаем клиент Discord
client1 = discord.Client(intents=intents)

# Функция для генерации ответа
async def generate_response(message_content):
    # Генерируем ответ с помощью модели OpenAI ChatCompletion
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        messages=[{"role": "user", "content": message_content}],
    )

    # Проверяем наличие выборок и сообщений в ответе
    if response.choices and response.choices[0].message and response.choices[0].message.content:
        response_content = response.choices[0].message.content
        return response_content
    else:
        # Обрабатываем случай, когда структура ответа неожиданна
        print("Неожиданная структура ответа:", response)
        return "Произошла ошибка при генерации ответа."

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
@client1.event
async def on_ready():
    print(f'{client1.user.name} has connected to Discord!')

# Функция, вызываемая при получении нового сообщения
@client1.event
async def on_message(message):
    # Если автор сообщения - бот, игнорируем его
    if message.author == client1.user:
        return

    # Если сообщение от пользователя с ID Vlad_ID или находится на нужном канале, обрабатываем его
    if (isinstance(message.channel, discord.DMChannel) and message.author.id in [Vlad_ID]) or message.channel.id == CHANNEL_ID:
        if len(message.content.strip()) > 0:
            # Генерируем ответ на основе содержимого сообщения пользователя
            response_content = await generate_response(message.content)
            # Отправляем ответ в канал, откуда пришло сообщение
            await send_response(message.channel, response_content)

# Запускаем клиент Discord
client1.run(token)