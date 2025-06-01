import time
import random
import json
import asyncio
import aiohttp
import isodate
import discord
from discord.ext import commands
from discord import app_commands

# Загрузка конфигурации из config.json
with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

TOKEN = config["token"]
PREFIX = config["prefix"]

YOUTUBE_API_KEY = "AIzaSyCNajbhrvtJEdBTgmyCjJSuO2rYlOJewOM"  # Замени на свой API-ключ

# Настройка интентов
intents = discord.Intents.default()
intents.message_content = True  # Необходимо для чтения содержимого сообщений

# Инициализация бота с нечувствительностью к регистру команд
bot = commands.Bot(command_prefix=PREFIX, intents=intents)

# Словарь "ключ-ответ"
replies = {
    "привет": "Привет! Рад тебя видеть!",
    "как дела?": "У меня всё отлично! А у тебя?",
    "что ты умеешь?": "Я умею отвечать на сообщения и выполнять команды!",
    "на чём ты написан?": "Я написан на языке Python"
}

# Список ключевых слов и их ответов
keyword_triggers = {
    "гойда": "Гойда! Братья и Сёстры!",
    "42": "ААА 42 БРАТУХА КЕМЕРОВСКАЯ ОБЛАСТЬ!!!",
    "zzz": "О, наш слоняра!"
}

# Сохраняем время старта бота
start_time = time.time()

# Список эмодзи для случайных реакций
reaction_emojis = ['🔥', '👍', '🎉','😂', '🤣', '😃', '😄', '😆', '😅', '😊', '😎',
    '😍', '😘', '🥰', '😋', '😜', '🤪', '😝', '😛', '🤗', '🤩', '🥳', '😏', '😌',
    '😔', '😷', '🤒', '🤕', '🤢', '🤮', '🤧', '🥺', '😢', '😭', '😤', '😡', '🤬',
    '😱', '😨', '😰', '😥', '😓', '😬', '😳', '🤭', '🤫', '🤔', '🤨', '😐', '😑',
    '😶', '🙄', '😯', '😦', '😧', '😮', '😲', '🥱', '😴', '😪', '😵', '😵‍💫',
    '🤯', '🤠', '🥸', '😈', '👿', '👹', '👺', '💀', '☠️', '👻', '👽', '👾', '🤖', '🎃',
    '😺', '😸', '😹', '😻', '😼', '😽', '🙀', '😿', '😾', '🐱']

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"✅ Бот запущен как {bot.user}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # Преобразуем содержимое сообщения в нижний регистр
    content = message.content.lower()

    # Проверка, был ли бот упомянут
    is_mentioned = bot.user in message.mentions

    # Проверка, является ли сообщение ответом на сообщение бота
    is_reply_to_bot = False
    if message.reference:
        try:
            replied_message = await message.channel.fetch_message(message.reference.message_id)
            if replied_message.author == bot.user:
                is_reply_to_bot = True
        except:
            pass  # Если сообщение не найдено, просто пропускаем

    # Проверка на упоминание имени бота в сообщении
    bot_names = ["qubert", "куберт"]
    is_name_in_message = any(name in content for name in bot_names)

    # Ответ на фразы, если бот упомянут, на него ответили или назвали по имени
    if is_mentioned or is_reply_to_bot or is_name_in_message:
        for key in replies:
            if key in content:
                await message.channel.send(replies[key])
                break

    # Ответ на ключевые слова независимо от упоминаний
    for keyword, response in keyword_triggers.items():
        if keyword in content:
            await message.channel.send(response)
            break

    # Случайная реакция с вероятностью 25%
    if random.random() < 0.25:
        emoji = random.choice(reaction_emojis)
        try:
            await message.add_reaction(emoji)
        except:
            pass

    await bot.process_commands(message)  # Обработка команд

# Функция форматирования времени в формат дн:ч:м:с
def format_uptime(seconds):
    days = seconds // 86400
    hours = (seconds % 86400) // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return f"{days}d {hours}h {minutes}m {seconds}s"

# Команда /uptime
@bot.tree.command(name="uptime", description="Показать, сколько времени работает бот")
async def uptime(interaction: discord.Interaction):
    uptime_seconds = int(time.time() - start_time)
    uptime_str = format_uptime(uptime_seconds)
    await interaction.response.send_message(f"Время работы бота: {uptime_str}")

# Команда /ping
@bot.tree.command(name="ping", description="Пинг-понг команда")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("Pong!")

# Команда /math — калькулятор
@bot.tree.command(name="math", description="Калькулятор")
@app_commands.describe(value1="Первое число", operator="Оператор (+, -, *, /, %, **)", value2="Второе число")
async def math(interaction: discord.Interaction, value1: str, operator: str, value2: str):
    try:
        num1 = float(value1)
        num2 = float(value2)

        if operator == "+":
            result = num1 + num2
        elif operator == "-":
            result = num1 - num2
        elif operator == "*":
            result = num1 * num2
        elif operator == "/":
            if num2 == 0:
                await interaction.response.send_message("**Ошибка:** деление на ноль!")
                return
            result = num1 / num2
        elif operator == "%":
            result = num1 % num2
        elif operator == "**":
            result = num1 ** num2
        else:
            await interaction.response.send_message("**Ошибка:** неизвестный оператор. Допустимые: +, -, *, /, %, **")
            return

        await interaction.response.send_message(f"Результат: {num1} {operator} {num2} = {result}")

    except ValueError:
        await interaction.response.send_message("**Ошибка:** Введите корректные числа.")

# Команда /roll — бросок костей
@bot.tree.command(name="roll", description="Бросить кости")
@app_commands.describe(количество="Количество костей", грани="Количество граней")
async def roll(interaction: discord.Interaction, количество: int, грани: int):
    if количество <= 0 or грани <= 0:
        await interaction.response.send_message("Введите положительные числа для количества и граней.")
        return
    результаты = [str(random.randint(1, грани)) for _ in range(количество)]
    await interaction.response.send_message(f"**Результаты броска:** {', '.join(результаты)}")

# Команда /8ball — магический шар
@bot.tree.command(name="8ball", description="Задать магический вопрос")
@app_commands.describe(вопрос="Ваш вопрос")
async def eightball(interaction: discord.Interaction, вопрос: str):
    ответы = [
        "Бесспорно.",
        "Предрешено.",
        "Никаких сомнений.",
        "Определённо да.",
        "Можешь быть уверен в этом.",
        "Мне кажется — 'да'.", "Вероятнее всего.",
        "Хорошие перспективы.",
        "Знаки говорят — 'да'.",
        "Да.",
        "Нет.",
        "Даже не думай.",
        "Мой ответ — 'нет'.",
        "По моим данным — 'нет'.",
        "Перспективы не очень хорошие.",
        "Весьма сомнительно."
    ]
    ответ = random.choice(ответы)
    await interaction.response.send_message(f"**Вопрос:** {вопрос}\n**Ответ:** {ответ}")

# Команда /guess — игра "Угадай число"
@bot.tree.command(name="guess", description="Угадай число от 1 до 100")
async def guess(interaction: discord.Interaction):
    число = random.randint(1, 100)
    попытки = 5

    await interaction.response.send_message(f"Я загадал число от 1 до 100. У тебя {попытки} попыток.")

    def check(m):
        return m.author.id == interaction.user.id and m.channel.id == interaction.channel.id

    while попытки > 0:
        try:
            сообщение = await bot.wait_for("message", timeout=15.0, check=check)
            предположение = int(сообщение.content)
        except ValueError:
            await interaction.channel.send("Введите целое число.")
            continue
        except asyncio.TimeoutError:
            await interaction.channel.send(f"{interaction.user.mention} Время вышло! Игра окончена.")
            return

        if предположение == число:
            await interaction.channel.send(f"Поздравляю, {interaction.user.mention}! Ты угадал число {число}!")
            return
        elif предположение < число:
            await interaction.channel.send("Моё число больше.")
        else:
            await interaction.channel.send("Моё число меньше.")

        попытки -= 1

    await interaction.channel.send(f"Увы, ты не угадал. Моё число было {число}.")

# Команда /randomsong
@bot.tree.command(name="randomsong", description="Получить случайную песню с YouTube")
async def random_song(interaction: discord.Interaction):
    await interaction.response.defer()

    # Cлова, по которым будем отфильтровывать в случайной музыке
    BAD_KEYWORDS = ["hindi", "bollywood", "punjabi", "bharat", "india", "desi", "bhojpuri", "jumpscares", "tutorial", "riffs", "parody", "ai", "live"]

    # 50% шанс что выпадает Эминем
    if random.random() < 0.5:
        search_term = random.choice([
            "Eminem"
        ])
    else:
        search_term = random.choice([
            "Eminem",
            "Limp Bizkit",
            "Linkin Park",
            "Slipknot",
            "Dr. Dre",
            "Static-X",
            "Avenged Sevenfold",
            "Megadeth",
            "Disturbed",
            "Styles of Beyond",
            "Fort Minor",
            "N.W.A",
            "Metallica",
            "Iron Maiden",
            "Black Sabbath",
            "Slayer",
            "Pantera",
            "Judas Priest",
            "Lamb of God",
            "System of a Down",
            "Mastodon",
            "Dope",
            "Skindred",
            "Rammstein",
            "Rob Zombie",
            "Mick Gordon",
            "Gorillaz",
            "I Prevail",
            "Twisted Sister",
            "Celldweller",
            "Sabaton",
            "Green Day",
            "Five Finger Death Punch"
        ])

    search_url = (
        f"https://www.googleapis.com/youtube/v3/search"
        f"?part=snippet&type=video&maxResults=5"
        f"&q={search_term}&relevanceLanguage=en&key={YOUTUBE_API_KEY}"
    )

    async with aiohttp.ClientSession() as session:
        async with session.get(search_url) as resp:
            search_data = await resp.json()

        if "items" not in search_data or len(search_data["items"]) == 0:
            await interaction.followup.send("**Ошибка:** Не удалось найти песню. Попробуй ещё раз.")
            return

        video_ids = [
            item["id"]["videoId"] 
            for item in search_data.get("items", []) 
            if "videoId" in item.get("id", {})
        ]
        
        videos_url = (
            f"https://www.googleapis.com/youtube/v3/videos"
            f"?part=contentDetails,snippet&id={','.join(video_ids)}&key={YOUTUBE_API_KEY}"
        )

        async with session.get(videos_url) as resp:
            videos_data = await resp.json()

    valid_videos = []
    for item in videos_data.get("items", []):
        video_id = item["id"]
        title = item["snippet"]["title"].lower()
        duration = item["contentDetails"]["duration"]

        if any(keyword in title for keyword in BAD_KEYWORDS):
            continue

        try:
            duration_seconds = isodate.parse_duration(duration).total_seconds()
        except:
            continue

        if 70 <= duration_seconds <= 600:
            valid_videos.append((video_id, item["snippet"]["title"]))

    if not valid_videos:
        await interaction.followup.send("**Ошибка:** Все подходящие видео были слишком короткими, длинными или не соответствовали фильтрам. Попробуй ещё раз.")
        return

    selected_id, selected_title = random.choice(valid_videos)
    youtube_url = f"https://www.youtube.com/watch?v={selected_id}"
    await interaction.followup.send(youtube_url)

# Запуск бота
bot.run(TOKEN)
