import math
import requests
import json
import uuid
from datetime import datetime, timedelta
import pytz
import asyncio
import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
import os
import random
import time
import threading

# Logging sozlash
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# API sozlamalari
TELEGRAM_TOKEN = "8178324958:AAEA-gSrfAnynGVdLb9vrhspcUBWZkvBJzI"  # Tokenni qo‘ying
GEMINI_API_KEY = "AIzaSyDA1bp80MVka2huOYr5fbvWbVDNfzTmGSk"
OPENWEATHER_API_KEY = "1cf6f4f3855774567a7f9826938b6a0c"
ADMIN_ID = 1807890167
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
MYMEMORY_API_URL = "https://api.mymemory.translated.net/get"
WEATHER_API_URL = "http://api.openweathermap.org/data/2.5/weather"
FORECAST_API_URL = "http://api.openweathermap.org/data/2.5/forecast"

# Fayl yo'llari
USERS_FILE = "users_data.json"
CONFIG_FILE = "config.json"
SURVEYS_FILE = "surveys.json"
BIRTHDAYS_FILE = "birthdays.json"
MOTIVATIONS_FILE = "motivations.json"
SUBSCRIPTIONS_FILE = "subscriptions.json"
RSA_FILE = "rsa_data.json"

# Valyuta sozlamalari
currency_rates = {"USD": 0, "RUB": 0, "KZT": 0}
DOLLAR_SIGN = "$"
RUB_SIGN = "₽"
KZT_SIGN = "₸"
SUM_SIGN = "so'm"

# Bot holati
class BotState:
    waiting_for_rate = False
    waiting_for_currency_type = False
    waiting_for_dollar_amount = False
    waiting_for_sum_to_dollar = False
    waiting_for_rub_amount = False
    waiting_for_sum_to_rub = False
    waiting_for_kzt_amount = False
    waiting_for_sum_to_kzt = False

bot_state = BotState()

# Bayroqlar
FLAGS = {"uz": "🇺🇿", "ru": "🇷🇺", "en": "🇬🇧", "ar": "🇸🇦", "tr": "🇹🇷", "kz": "🇰🇿", "cn": "🇨🇳", "jp": "🇯🇵", "de": "🇩🇪",
         "fr": "🇫🇷"}

# O'zbekiston viloyatlari va koordinatalari
REGIONS = {
    "Toshkent": {"lat": 41.2995, "lon": 69.2401},
    "Andijon": {"lat": 40.8154, "lon": 72.2839},
    "Buxoro": {"lat": 39.7676, "lon": 64.4556},
    "Farg'ona": {"lat": 40.3734, "lon": 71.7978},
    "Jizzax": {"lat": 40.1233, "lon": 67.8286},
    "Xorazm": {"lat": 41.5539, "lon": 60.6218},
    "Namangan": {"lat": 41.0000, "lon": 71.6667},
    "Navoiy": {"lat": 40.1000, "lon": 65.3667},
    "Qashqadaryo": {"lat": 38.8333, "lon": 65.8000},
    "Samarqand": {"lat": 39.6542, "lon": 66.9597},
    "Sirdaryo": {"lat": 40.8167, "lon": 68.6667},
    "Surxondaryo": {"lat": 37.9500, "lon": 67.5667},
    "Qoraqalpog'iston": {"lat": 42.4667, "lon": 59.6167}
}

# Vaqt zonalari
TIMEZONES = {
    "O'zbekiston": {"tz": "Asia/Tashkent", "flag": "🇺🇿"},
    "Qozog'iston": {"tz": "Asia/Almaty", "flag": "🇰🇿"},
    "Rossiya": {"tz": "Europe/Moscow", "flag": "🇷🇺"},
    "Angliya": {"tz": "Europe/London", "flag": "🇬🇧"},
    "Saudiya Arabistoni": {"tz": "Asia/Riyadh", "flag": "🇸🇦"},
    "Turkiya": {"tz": "Europe/Istanbul", "flag": "🇹🇷"},
    "Xitoy": {"tz": "Asia/Shanghai", "flag": "🇨🇳"},
    "Yaponiya": {"tz": "Asia/Tokyo", "flag": "🇯🇵"},
    "Germaniya": {"tz": "Europe/Berlin", "flag": "🇩🇪"},
    "Fransiya": {"tz": "Europe/Paris", "flag": "🇫🇷"}
}

# Transliteratsiya jadvallari
TRANSLIT_TABLES = {
    "uz": {
        "lotin_to_kiril": {
            "a": "а", "b": "б", "d": "д", "e": "э", "f": "ф", "g": "г", "h": "ҳ",
            "i": "и", "j": "ж", "k": "к", "l": "л", "m": "м", "n": "н", "o": "о",
            "p": "п", "q": "қ", "r": "р", "s": "с", "t": "т", "u": "у", "v": "в",
            "x": "х", "y": "й", "z": "з",
            "o'": "ў", "g'": "ғ", "sh": "ш", "ch": "ч",
            "A": "А", "B": "Б", "D": "Д", "E": "Э", "F": "Ф", "G": "Г", "H": "Ҳ",
            "I": "И", "J": "Ж", "K": "К", "L": "Л", "M": "М", "N": "Н", "O": "О",
            "P": "П", "Q": "Қ", "R": "Р", "S": "С", "T": "Т", "U": "У", "V": "В",
            "X": "Х", "Y": "Й", "Z": "З",
            "O'": "Ў", "G'": "Ғ", "Sh": "Ш", "SH": "Ш", "Ch": "Ч", "CH": "Ч",
            "o‘": "ў", "g‘": "ғ", "O‘": "Ў", "G‘": "Ғ"
        },
        "kiril_to_lotin": {
            "а": "a", "б": "b", "д": "d", "э": "e", "ф": "f", "г": "g", "ҳ": "h",
            "и": "i", "ж": "j", "к": "k", "л": "l", "м": "m", "н": "n", "о": "o",
            "п": "p", "қ": "q", "р": "r", "с": "s", "т": "t", "у": "u", "в": "v",
            "х": "x", "й": "y", "з": "z",
            "ў": "o'", "ғ": "g'", "ш": "sh", "ч": "ch",
            "А": "A", "Б": "B", "Д": "D", "Э": "E", "Ф": "F", "Г": "G", "Ҳ": "H",
            "И": "I", "Ж": "J", "К": "K", "Л": "L", "М": "M", "Н": "N", "О": "O",
            "П": "П", "Қ": "Q", "Р": "R", "С": "S", "Т": "Т", "У": "U", "В": "V",
            "Х": "X", "Й": "Y", "З": "Z",
            "Ў": "O'", "Ғ": "G'", "Ш": "Sh", "Ч": "Ch"
        }
    }
}

# Ma'lumotlarni boshqarish
users_data = {}
surveys_data = {}
birthdays_data = {}
motivations_data = {}
subscriptions_data = {}
rsa_data = {}

def load_config():
    global currency_rates
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as file:
            config = json.load(file)
            currency_rates = config.get('currency_rates', {"USD": 0, "RUB": 0, "KZT": 0})
    except (FileNotFoundError, json.JSONDecodeError):
        with open(CONFIG_FILE, 'w', encoding='utf-8') as file:
            json.dump({'currency_rates': {"USD": 0, "RUB": 0, "KZT": 0}}, file, indent=4, ensure_ascii=False)

def save_config():
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as file:
            json.dump({'currency_rates': currency_rates}, file, indent=4, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Konfiguratsiyani saqlashda xato: {e}")

def load_users_data():
    global users_data
    try:
        with open(USERS_FILE, 'r', encoding='utf-8') as file:
            users_data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        users_data = {}
        with open(USERS_FILE, 'w', encoding='utf-8') as file:
            json.dump(users_data, file, indent=4, ensure_ascii=False)

def save_users_data():
    try:
        with open(USERS_FILE, 'w', encoding='utf-8') as file:
            json.dump(users_data, file, indent=4, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Foydalanuvchi ma'lumotlarini saqlashda xato: {e}")

def load_surveys():
    global surveys_data
    try:
        with open(SURVEYS_FILE, 'r', encoding='utf-8') as file:
            surveys_data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        surveys_data = {}
        with open(SURVEYS_FILE, 'w', encoding='utf-8') as file:
            json.dump(surveys_data, file, indent=4, ensure_ascii=False)

def save_surveys():
    try:
        with open(SURVEYS_FILE, 'w', encoding='utf-8') as file:
            json.dump(surveys_data, file, indent=4, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Sorovnoma ma'lumotlarini saqlashda xato: {e}")

def load_birthdays():
    global birthdays_data
    try:
        with open(BIRTHDAYS_FILE, 'r', encoding='utf-8') as file:
            birthdays_data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        birthdays_data = {}
        with open(BIRTHDAYS_FILE, 'w', encoding='utf-8') as file:
            json.dump(birthdays_data, file, indent=4, ensure_ascii=False)

def save_birthdays():
    try:
        with open(BIRTHDAYS_FILE, 'w', encoding='utf-8') as file:
            json.dump(birthdays_data, file, indent=4, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Tug'ilgan kun ma'lumotlarini saqlashda xato: {e}")

def load_motivations():
    global motivations_data
    try:
        with open(MOTIVATIONS_FILE, 'r', encoding='utf-8') as file:
            motivations_data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        motivations_data = {"motivations": []}
        with open(MOTIVATIONS_FILE, 'w', encoding='utf-8') as file:
            json.dump(motivations_data, file, indent=4, ensure_ascii=False)

def save_motivations():
    try:
        with open(MOTIVATIONS_FILE, 'w', encoding='utf-8') as file:
            json.dump(motivations_data, file, indent=4, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Motivatsion so'zlarni saqlashda xato: {e}")

def load_subscriptions():
    global subscriptions_data
    try:
        with open(SUBSCRIPTIONS_FILE, 'r', encoding='utf-8') as file:
            subscriptions_data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        subscriptions_data = {"subscriptions": []}
        with open(SUBSCRIPTIONS_FILE, 'w', encoding='utf-8') as file:
            json.dump(subscriptions_data, file, indent=4, ensure_ascii=False)

def save_subscriptions():
    try:
        with open(SUBSCRIPTIONS_FILE, 'w', encoding='utf-8') as file:
            json.dump(subscriptions_data, file, indent=4, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Obuna ma'lumotlarini saqlashda xato: {e}")

def load_rsa_data():
    global rsa_data
    try:
        with open(RSA_FILE, 'r', encoding='utf-8') as file:
            rsa_data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        rsa_data = {}
        with open(RSA_FILE, 'w', encoding='utf-8') as file:
            json.dump(rsa_data, file, indent=4, ensure_ascii=False)

def save_rsa_data():
    try:
        with open(RSA_FILE, 'w', encoding='utf-8') as file:
            json.dump(rsa_data, file, indent=4, ensure_ascii=False)
    except Exception as e:
        logger.error(f"RSA ma'lumotlarini saqlashda xato: {e}")

def update_user_data(user_id, username, first_name, message=None):
    user_id_str = str(user_id)
    if user_id_str not in users_data:
        users_data[user_id_str] = {
            "username": username or "None",
            "first_name": first_name,
            "messages": [],
            "is_active": True
        }
    if message:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        users_data[user_id_str]["messages"].append({
            "text": message,
            "timestamp": timestamp
        })
    save_users_data()

# API xizmatlari
def query_gemini(text):
    try:
        headers = {"Content-Type": "application/json", "x-goog-api-key": GEMINI_API_KEY}
        payload = {"contents": [{"parts": [{"text": text}]}]}
        response = requests.post(GEMINI_API_URL, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        result = response.json()
        if "candidates" in result and result["candidates"]:
            return result["candidates"][0]["content"]["parts"][0]["text"]
        return "Javob topilmadi."
    except requests.exceptions.RequestException as e:
        return f"Gemini xatosi: {str(e)}"

def mymemory_translate(text, source_lang, target_lang):
    try:
        params = {"q": text, "langpair": f"{source_lang}|{target_lang}"}
        response = requests.get(MYMEMORY_API_URL, params=params, timeout=10)
        response.raise_for_status()
        result = response.json()
        if result["responseStatus"] == 200 and "translatedText" in result["responseData"]:
            return result["responseData"]["translatedText"]
        return "Tarjima xatosi."
    except requests.exceptions.RequestException as e:
        return f"Tarjima xatosi: {str(e)}"

def get_weather(lat, lon):
    try:
        params = {
            "lat": lat,
            "lon": lon,
            "appid": OPENWEATHER_API_KEY,
            "units": "metric",
            "lang": "uz"
        }
        response = requests.get(WEATHER_API_URL, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"Ob-havo xatosi: {str(e)}"}

def get_forecast(lat, lon):
    try:
        params = {
            "lat": lat,
            "lon": lon,
            "appid": OPENWEATHER_API_KEY,
            "units": "metric",
            "lang": "uz"
        }
        response = requests.get(FORECAST_API_URL, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"Prognoz xatosi: {str(e)}"}

# RSA shifrlash
def is_prime(n):
    if n <= 1:
        return False
    if n <= 3:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True

def is_coprime(a, b):
    return math.gcd(a, b) == 1

def mod_inverse(e, phi):
    for d in range(3, phi):
        if (d * e) % phi == 1:
            return d
    raise ValueError("mod_inverse topilmadi")

def generate_keys(p, q):
    if not is_prime(p) or not is_prime(q):
        raise ValueError("p va q tub sonlar bo'lishi kerak!")
    if p == q:
        raise ValueError("p va q bir xil bo'lmasligi kerak!")
    n = p * q
    phi = (p - 1) * (q - 1)
    e = 65537
    if not is_coprime(e, phi):
        e = 3
        while e < phi:
            if is_coprime(e, phi):
                break
            e += 2
    d = mod_inverse(e, phi)
    return (e, n), (d, n)

def encrypt(public_key, plaintext):
    e, n = public_key
    cipher = [pow(ord(char), e, n) for char in plaintext]
    return cipher

def decrypt(private_key, ciphertext):
    d, n = private_key
    cipher_list = list(map(int, ciphertext.split(',')))
    plain = [chr(pow(char, d, n)) for char in cipher_list]
    return ''.join(plain)


# Transliteratsiya
def detect_script(text):
    kiril_chars = set("абвгдеёжзийклмнопрстуфхцчшщъыьэюяўғқҳ")
    lotin_chars = set("o'g'şç")
    kiril_count = sum(1 for char in text.lower() if char in kiril_chars)
    lotin_count = sum(1 for char in text.lower() if char in lotin_chars)
    return "kiril" if kiril_count > lotin_count else "lotin"

def transliterate(text, source_lang, target_lang, source_script=None, target_script=None):
    if source_lang == target_lang and source_lang in TRANSLIT_TABLES:
        if source_script is None:
            source_script = detect_script(text)
        if target_script is None:
            target_script = "lotin" if source_script == "kiril" else "kiril"
        direction = f"{source_script}_to_{target_script}"
        table = TRANSLIT_TABLES[source_lang][direction]
        for src, dest in sorted(table.items(), key=lambda x: len(x[0]), reverse=True):
            text = text.replace(src, dest)
        return text
    return text


# Valyuta formatlash
def format_currency(amount):
    return f"{amount:,.2f}".replace(',', ' ')

# Motivatsiya funksiyalari
def register_user(user_id, username):
    user_id_str = str(user_id)
    if user_id_str not in users_data:
        users_data[user_id_str] = {
            "username": username or "None",
            "first_name": username,
            "messages": [],
            "is_active": True,
            "joined_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        save_users_data()
        return True
    return False

def add_motivation(text, user_id, username):
    motivation_id = len(motivations_data.get("motivations", [])) + 1
    new_motivation = {
        "id": motivation_id,
        "text": text,
        "author_id": user_id,
        "author_username": username,
        "added_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": "pending",
        "likes": 0,
        "liked_by": []
    }
    motivations_data.setdefault("motivations", []).append(new_motivation)
    save_motivations()
    return motivation_id

def approve_motivation(motivation_id):
    for motivation in motivations_data.get("motivations", []):
        if motivation["id"] == motivation_id:
            motivation["status"] = "approved"
            save_motivations()
            return True
    return False

def reject_motivation(motivation_id):
    for motivation in motivations_data.get("motivations", []):
        if motivation["id"] == motivation_id:
            motivation["status"] = "rejected"
            save_motivations()
            return True
    return False

def edit_motivation(motivation_id, new_text):
    for motivation in motivations_data.get("motivations", []):
        if motivation["id"] == motivation_id:
            motivation["text"] = new_text
            save_motivations()
            return True
    return False

def delete_motivation(motivation_id):
    motivations_data["motivations"] = [m for m in motivations_data.get("motivations", []) if m["id"] != motivation_id]
    save_motivations()
    return True

def like_motivation(motivation_id, user_id):
    for motivation in motivations_data.get("motivations", []):
        if motivation["id"] == motivation_id:
            user_id_str = str(user_id)
            if user_id_str in motivation["liked_by"]:
                motivation["liked_by"].remove(user_id_str)
                motivation["likes"] -= 1
                save_motivations()
                return False
            else:
                motivation["liked_by"].append(user_id_str)
                motivation["likes"] += 1
                save_motivations()
                return True
    return None

def subscribe_to_motivation(user_id, frequency, time_to_send):
    subscriptions_data["subscriptions"] = [s for s in subscriptions_data.get("subscriptions", []) if s["user_id"] != user_id]
    subscriptions_data.setdefault("subscriptions", []).append({
        "user_id": user_id,
        "frequency": frequency,
        "time": time_to_send,
        "last_sent": None
    })
    save_subscriptions()
    return True

def get_random_motivation():
    approved_motivations = [m for m in motivations_data.get("motivations", []) if m["status"] == "approved"]
    if approved_motivations:
        return random.choice(approved_motivations)
    return None

def is_admin(user_id):
    return user_id == ADMIN_ID

async def send_scheduled_motivations(application):
    while True:
        try:
            now = datetime.now()
            current_time = now.strftime("%H:%M")
            current_day = now.day
            current_week = now.isocalendar()[1]
            current_month = now.month

            for sub in subscriptions_data.get("subscriptions", []):
                user_id = sub["user_id"]
                frequency = sub["frequency"]
                time_to_send = sub["time"]

                if time_to_send == current_time:
                    send_motivation = False
                    if frequency == "daily":
                        send_motivation = True
                    elif frequency == "weekly" and now.weekday() == 0:
                        send_motivation = True
                    elif frequency == "monthly" and current_day == 1:
                        send_motivation = True

                    if send_motivation:
                        motivation = get_random_motivation()
                        if motivation:
                            keyboard = [
                                [
                                    InlineKeyboardButton(f"❤️ {motivation['likes']}", callback_data=f"motiv_like_{motivation['id']}"),
                                    InlineKeyboardButton("🔄 Ulashish", switch_inline_query=f"Motivatsiya: {motivation['text']}")
                                ]
                            ]
                            try:
                                await application.bot.send_message(
                                    user_id,
                                    f"📌 Kunlik motivatsiyangiz:\n\n{motivation['text']}\n\n👤 Muallif: @{motivation['author_username']}",
                                    reply_markup=InlineKeyboardMarkup(keyboard)
                                )
                                sub["last_sent"] = now.strftime("%Y-%m-%d %H:%M:%S")
                            except Exception as e:
                                logger.error(f"Xabar yuborishda xato {user_id}: {e}")

            save_subscriptions()
            await asyncio.sleep(60)
        except Exception as e:
            logger.error(f"Rejalashtiruvchida xato: {e}")
            await asyncio.sleep(60)

# Inline menyular
def main_menu(user_id=None):
    keyboard = [
        [
            InlineKeyboardButton("🤖 Yordamchi Chat", callback_data='chat'),
            InlineKeyboardButton("📞 Aloqa", callback_data='aloqa'),
        ],
        [
            InlineKeyboardButton("🌤️ Ob-havo", callback_data='weather'),
            InlineKeyboardButton("🕒 Soat va Vaqt", callback_data='timezone'),
        ],
        [
            InlineKeyboardButton("📈 Iqtisodiy Statistika", callback_data='economics'),
            InlineKeyboardButton("📝 Sorovnoma", callback_data='survey')
        ],
        [
            InlineKeyboardButton("🎂 Tug'ilgan Kun", callback_data='birthday'),
            InlineKeyboardButton("🔒 RSA Shifrlash", callback_data='rsa'),
        ],
        [
            InlineKeyboardButton("🌐 Tarjimon", callback_data='tarjima'),
            InlineKeyboardButton("🔤 Transliteratsiya", callback_data='translit'),
        ],
        [
            InlineKeyboardButton("💬 Motivatsiya", callback_data='motivatsiya'),
            InlineKeyboardButton("💸 Valyuta Konvertori", callback_data='currency')
        ]
    ]
    if user_id and is_admin(user_id):
        keyboard.append([InlineKeyboardButton("📋 Admin Panel", callback_data='admin')])
    return InlineKeyboardMarkup(keyboard)

def currency_menu(user_id):
    keyboard = []
    if user_id == ADMIN_ID:
        keyboard.append([InlineKeyboardButton("💰 Kursni belgilash", callback_data='currency_set_rate')])
    keyboard.append([InlineKeyboardButton("🔄 Konvertatsiya", callback_data='currency_convert')])
    keyboard.append([InlineKeyboardButton("🔙 Orqaga", callback_data='main')])
    return InlineKeyboardMarkup(keyboard)

def currency_set_rate_menu():
    keyboard = [
        [InlineKeyboardButton("💵 USD kursi", callback_data='set_rate_usd')],
        [InlineKeyboardButton(f"{RUB_SIGN} RUB kursi", callback_data='set_rate_rub')],
        [InlineKeyboardButton(f"{KZT_SIGN} KZT kursi", callback_data='set_rate_kzt')],
        [InlineKeyboardButton("🔙 Orqaga", callback_data='currency')]
    ]
    return InlineKeyboardMarkup(keyboard)

def conversion_menu():
    keyboard = [
        [
            InlineKeyboardButton("💵 Dollar → So'm", callback_data='currency_dollar_to_sum'),
            InlineKeyboardButton("💴 So'm → Dollar", callback_data='currency_sum_to_dollar')
        ],
        [
            InlineKeyboardButton(f"{RUB_SIGN} Rubl → So'm", callback_data='currency_rub_to_sum'),
            InlineKeyboardButton(f"{SUM_SIGN} So'm → Rubl", callback_data='currency_sum_to_rub')
        ],
        [
            InlineKeyboardButton(f"{KZT_SIGN} Tenge → So'm", callback_data='currency_kzt_to_sum'),
            InlineKeyboardButton(f"{SUM_SIGN} So'm → Tenge", callback_data='currency_sum_to_kzt')
        ],
        [InlineKeyboardButton("🔙 Orqaga", callback_data='currency')]
    ]
    return InlineKeyboardMarkup(keyboard)

def weather_menu():
    keyboard = [
        [InlineKeyboardButton(region, callback_data=f'weather_{region}') for region in list(REGIONS.keys())[:4]],
        [InlineKeyboardButton(region, callback_data=f'weather_{region}') for region in list(REGIONS.keys())[4:8]],
        [InlineKeyboardButton(region, callback_data=f'weather_{region}') for region in list(REGIONS.keys())[8:12]],
        [InlineKeyboardButton(list(REGIONS.keys())[12], callback_data=f'weather_{list(REGIONS.keys())[12]}')],
        [InlineKeyboardButton("🔙 Orqaga", callback_data='main')]
    ]
    return InlineKeyboardMarkup(keyboard)

def weather_detail_menu(region):
    keyboard = [
        [InlineKeyboardButton("Bugungi ob-havo", callback_data=f'weather_today_{region}')],
        [InlineKeyboardButton("Ertangi ob-havo", callback_data=f'weather_tomorrow_{region}')],
        [InlineKeyboardButton("7 kunlik prognoz", callback_data=f'weather_week_{region}')],
        [InlineKeyboardButton("🔙 Orqaga", callback_data='weather')]
    ]
    return InlineKeyboardMarkup(keyboard)

def timezone_menu():
    keyboard = [
        [InlineKeyboardButton(f"{TIMEZONES[country]['flag']} {country}", callback_data=f'timezone_{country}') for
         country in list(TIMEZONES.keys())[:5]],
        [InlineKeyboardButton(f"{TIMEZONES[country]['flag']} {country}", callback_data=f'timezone_{country}') for
         country in list(TIMEZONES.keys())[5:]],
        [InlineKeyboardButton("🔙 Orqaga", callback_data='main')]
    ]
    return InlineKeyboardMarkup(keyboard)

def survey_menu():
    keyboard = [
        [InlineKeyboardButton("📝 Yangi sorovnoma", callback_data='survey_new')],
        [InlineKeyboardButton("📊 Natijalarni ko'rish", callback_data='survey_results')],
        [InlineKeyboardButton("🔙 Orqaga", callback_data='main')]
    ]
    return InlineKeyboardMarkup(keyboard)

def birthday_menu():
    keyboard = [
        [InlineKeyboardButton("🎂 Tug'ilgan kunni kiritish", callback_data='birthday_set')],
        [InlineKeyboardButton("📅 Ma'lumotni ko'rish", callback_data='birthday_view')],
        [InlineKeyboardButton("🔙 Orqaga", callback_data='main')]
    ]
    return InlineKeyboardMarkup(keyboard)

def rsa_menu():
    keyboard = [
        [InlineKeyboardButton("🔒 Shifrlash", callback_data='rsa_encrypt')],
        [InlineKeyboardButton("🔓 Deshifrlash", callback_data='rsa_decrypt')],
        [InlineKeyboardButton("🔙 Orqaga", callback_data='main')]
    ]
    return InlineKeyboardMarkup(keyboard)

def rsa_list_menu(rsa_list, page=1, per_page=5):
    total_pages = math.ceil(len(rsa_list) / per_page)
    start = (page - 1) * per_page
    end = start + per_page
    keyboard = []

    for rsa_id, rsa_data in list(rsa_list.items())[start:end]:
        keyboard.append([InlineKeyboardButton(
            f"Matn: {rsa_data['plaintext'][:20]}... (ID: {rsa_id[:8]})",
            callback_data=f'rsa_view_{rsa_id}'
        )])

    nav_buttons = []
    if page > 1:
        nav_buttons.append(InlineKeyboardButton("⬅️ Oldingi", callback_data=f'rsa_page_{page - 1}'))
    if page < total_pages:
        nav_buttons.append(InlineKeyboardButton("Keyingi ➡️", callback_data=f'rsa_page_{page + 1}'))
    if nav_buttons:
        keyboard.append(nav_buttons)

    keyboard.append([InlineKeyboardButton("🔙 Orqaga", callback_data='admin')])
    return InlineKeyboardMarkup(keyboard)

def rsa_detail_menu(rsa_id, user_id):
    keyboard = []
    if user_id == ADMIN_ID:
        keyboard.append([
            InlineKeyboardButton("✏️ Tahrirlash", callback_data=f'rsa_edit_{rsa_id}'),
            InlineKeyboardButton("🗑 O'chirish", callback_data=f'rsa_delete_{rsa_id}')
        ])
    keyboard.append([InlineKeyboardButton("🔙 Orqaga", callback_data='admin_rsa')])
    return InlineKeyboardMarkup(keyboard)


def tarjima_menu():
    keyboard = [
        [
            InlineKeyboardButton(f"{FLAGS['uz']} O'zbek → {FLAGS['ru']} Rus", callback_data='tarjima_uz_ru'),
            InlineKeyboardButton(f"{FLAGS['ru']} Rus → {FLAGS['uz']} O'zbek", callback_data='tarjima_ru_uz')
        ],
        [
            InlineKeyboardButton(f"{FLAGS['uz']} O'zbek → {FLAGS['en']} Ingliz", callback_data='tarjima_uz_en'),
            InlineKeyboardButton(f"{FLAGS['en']} Ingliz → {FLAGS['uz']} O'zbek", callback_data='tarjima_en_uz')
        ],
        [
            InlineKeyboardButton(f"{FLAGS['uz']} O'zbek → {FLAGS['ar']} Arab", callback_data='tarjima_uz_ar'),
            InlineKeyboardButton(f"{FLAGS['ar']} Arab → {FLAGS['uz']} O'zbek", callback_data='tarjima_ar_uz')
        ],
        [
            InlineKeyboardButton(f"{FLAGS['uz']} O'zbek → {FLAGS['tr']} Turk", callback_data='tarjima_uz_tr'),
            InlineKeyboardButton(f"{FLAGS['tr']} Turk → {FLAGS['uz']} O'zbek", callback_data='tarjima_tr_uz')
        ],
        [InlineKeyboardButton("🔙 Orqaga", callback_data='main')]
    ]
    return InlineKeyboardMarkup(keyboard)


def translit_menu():
    keyboard = [
        [
            InlineKeyboardButton(f"{FLAGS['uz']} Lotin → Kiril", callback_data='translit_uz_lotin_kiril'),
            InlineKeyboardButton(f"{FLAGS['uz']} Kiril → Lotin", callback_data='translit_uz_kiril_lotin')
        ],
        [InlineKeyboardButton("🔙 Orqaga", callback_data='main')]
    ]
    return InlineKeyboardMarkup(keyboard)



def motivation_menu(user_id):
    keyboard = [
        [InlineKeyboardButton("🔥 Motivatsiya olish", callback_data='motiv_get')],
        [InlineKeyboardButton("➕ Motivatsiya qo'shish", callback_data='motiv_add')],
        [InlineKeyboardButton("🔔 Obuna bo'lish", callback_data='motiv_subscribe')],
        [InlineKeyboardButton("🔙 Orqaga", callback_data='main')]
    ]
    if is_admin(user_id):
        keyboard.insert(0, [InlineKeyboardButton("📝 Tasdiqlanmagan motivatsiyalar", callback_data='motiv_pending')])
    return InlineKeyboardMarkup(keyboard)

def subscription_frequency_menu():
    keyboard = [
        [InlineKeyboardButton("📅 Har kuni", callback_data='motiv_sub_daily')],
        [InlineKeyboardButton("📅 Har hafta", callback_data='motiv_sub_weekly')],
        [InlineKeyboardButton("📅 Har oy", callback_data='motiv_sub_monthly')],
        [InlineKeyboardButton("🔙 Orqaga", callback_data='motivatsiya')]
    ]
    return InlineKeyboardMarkup(keyboard)

def admin_menu():
    keyboard = [
        [
            InlineKeyboardButton("📋 Foydalanuvchilar", callback_data='admin_users'),
            InlineKeyboardButton("📊 Statistika", callback_data='admin_stats')
        ],
        [
            InlineKeyboardButton("🗑 O'chirish", callback_data='admin_delete_user'),
            InlineKeyboardButton("🚫 Bloklash", callback_data='admin_block_user')
        ],
        [
            InlineKeyboardButton("💬 Xabarlarni ko'rish", callback_data='admin_messages'),
            InlineKeyboardButton("📝 Motivatsiyalarni boshqarish", callback_data='admin_motivations')
        ],
        [
            InlineKeyboardButton("🔒 RSA ma'lumotlari", callback_data='admin_rsa'),
            InlineKeyboardButton("🔙 Orqaga", callback_data='main')
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

# Buyruqlar
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    register_user(user.id, user.username or user.first_name)
    update_user_data(user.id, user.username, user.first_name)
    welcome_text = "Salom! Aziz yordamchi botiga xush kelibsiz.\nQuyidagi bo'limlardan birini tanlang:"
    if user.id == ADMIN_ID:
        welcome_text += f"\nHozirgi kurslar:\n"
        welcome_text += f"💵 {currency_rates['USD']} so'm = 1{DOLLAR_SIGN}\n"
        welcome_text += f"{RUB_SIGN} {currency_rates['RUB']} so'm = 1{RUB_SIGN}\n"
        welcome_text += f"{KZT_SIGN} {currency_rates['KZT']} so'm = 1{KZT_SIGN}"
    else:
        welcome_text += f"\nHozirgi kurslar:\n"
        if currency_rates["USD"] > 0:
            welcome_text += f"💵 1{DOLLAR_SIGN} = {currency_rates['USD']} so'm\n"
        else:
            welcome_text += f"💵 USD kursi belgilanmagan\n"
        if currency_rates["RUB"] > 0:
            welcome_text += f"{RUB_SIGN} 1{RUB_SIGN} = {currency_rates['RUB']} so'm\n"
        else:
            welcome_text += f"{RUB_SIGN} RUB kursi belgilanmagan\n"
        if currency_rates["KZT"] > 0:
            welcome_text += f"{KZT_SIGN} 1{KZT_SIGN} = {currency_rates['KZT']} so'm\n"
        else:
            welcome_text += f"{KZT_SIGN} KZT kursi belgilanmagan"
    await update.message.reply_text(welcome_text, reply_markup=main_menu(user.id))
    context.user_data['state'] = None

async def aziz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Admin panel uchun parolni kiriting:")
    context.user_data['state'] = 'admin_parol_kutish'

# Tugma callback
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = update.effective_user
    update_user_data(user.id, user.username, user.first_name)

    if query.data == 'motivatsiya':
        await query.message.reply_text(
            "💬 Motivatsion va hikmatli so'zlar bo'limi!\nTanlang:",
            reply_markup=motivation_menu(user.id)
        )
        context.user_data['state'] = 'motivatsiya'

    elif query.data == 'motiv_get':
        motivation = get_random_motivation()
        if not motivation:
            await query.message.reply_text("Hozircha tasdiqlangan motivatsiyalar yo'q.", reply_markup=motivation_menu(user.id))
            return
        keyboard = [
            [
                InlineKeyboardButton(f"❤️ {motivation['likes']}", callback_data=f"motiv_like_{motivation['id']}"),
                InlineKeyboardButton("🔄 Ulashish", switch_inline_query=f"Motivatsiya: {motivation['text']}")
            ]
        ]
        await query.message.reply_text(
            f"📌 Motivatsiya:\n\n{motivation['text']}\n\n👤 Muallif: @{motivation['author_username']}",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        context.user_data['state'] = 'motivatsiya'

    elif query.data == 'motiv_add':
        await query.message.reply_text(
            "Iltimos, motivatsiyangizni yuboring:",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Orqaga", callback_data='motivatsiya')]])
        )
        context.user_data['state'] = 'motiv_add_text'

    elif query.data == 'motiv_subscribe':
        await query.message.reply_text(
            "Motivatsiya olish davriyligini tanlang:",
            reply_markup=subscription_frequency_menu()
        )
        context.user_data['state'] = 'motiv_subscribe'

    elif query.data.startswith('motiv_sub_'):
        frequency = query.data.split('_')[-1]
        context.user_data['motiv_frequency'] = frequency
        await query.message.reply_text(
            "Motivatsiyani qaysi vaqtda olishni istaysiz? (Masalan: 08:00)",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Orqaga", callback_data='motivatsiya')]])
        )
        context.user_data['state'] = 'motiv_sub_time'

    elif query.data == 'motiv_pending' and is_admin(user.id):
        pending = [m for m in motivations_data.get("motivations", []) if m["status"] == "pending"]
        if not pending:
            await query.message.reply_text("Tasdiqlanmagan motivatsiyalar yo'q.", reply_markup=motivation_menu(user.id))
            return
        for motivation in pending:
            keyboard = [
                [
                    InlineKeyboardButton("✅ Tasdiqlash", callback_data=f"motiv_approve_{motivation['id']}"),
                    InlineKeyboardButton("❌ Bekor qilish", callback_data=f"motiv_reject_{motivation['id']}")
                ],
                [InlineKeyboardButton("✏️ Tahrirlash", callback_data=f"motiv_edit_{motivation['id']}")]
            ]
            await query.message.reply_text(
                f"ID: {motivation['id']}\nMuallif: @{motivation['author_username']}\nSana: {motivation['added_date']}\n\nText: {motivation['text']}",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        context.user_data['state'] = 'motiv_pending'

    elif query.data.startswith('motiv_approve_') and is_admin(user.id):
        motivation_id = int(query.data.split('_')[-1])
        if approve_motivation(motivation_id):
            await query.message.edit_text("✅ Motivatsiya tasdiqlandi!")
        else:
            await query.message.edit_text("⚠️ Motivatsiya topilmadi.")

    elif query.data.startswith('motiv_reject_') and is_admin(user.id):
        motivation_id = int(query.data.split('_')[-1])
        if reject_motivation(motivation_id):
            await query.message.edit_text("❌ Motivatsiya bekor qilindi!")
        else:
            await query.message.edit_text("⚠️ Motivatsiya topilmadi.")

    elif query.data.startswith('motiv_edit_') and is_admin(user.id):
        motivation_id = int(query.data.split('_')[-1])
        context.user_data['edit_motiv_id'] = motivation_id
        await query.message.reply_text(
            "Yangi motivatsiya matnini kiriting:",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Orqaga", callback_data='motiv_pending')]])
        )
        context.user_data['state'] = 'motiv_edit_text'

    elif query.data.startswith('motiv_like_'):
        motivation_id = int(query.data.split('_')[-1])
        result = like_motivation(motivation_id, user.id)
        for motivation in motivations_data.get("motivations", []):
            if motivation["id"] == motivation_id:
                keyboard = [
                    [
                        InlineKeyboardButton(f"❤️ {motivation['likes']}", callback_data=f"motiv_like_{motivation['id']}"),
                        InlineKeyboardButton("🔄 Ulashish", switch_inline_query=f"Motivatsiya: {motivation['text']}")
                    ]
                ]
                await query.message.edit_reply_markup(reply_markup=InlineKeyboardMarkup(keyboard))
                break
        if result is True:
            await query.answer("❤️ Like qo'shildi!")
        elif result is False:
            await query.answer("Like olib tashlandi!")
        else:
            await query.answer("Xatolik yuz berdi!")

    elif query.data == 'currency':
        welcome_text = "Valyuta konvertatsiya bo'limiga xush kelibsiz.\nHozirgi kurslar:\n"
        if currency_rates["USD"] > 0:
            welcome_text += f"💵 1{DOLLAR_SIGN} = {currency_rates['USD']} so'm\n"
        else:
            welcome_text += f"💵 USD kursi belgilanmagan\n"
        if currency_rates["RUB"] > 0:
            welcome_text += f"{RUB_SIGN} 1{RUB_SIGN} = {currency_rates['RUB']} so'm\n"
        else:
            welcome_text += f"{RUB_SIGN} RUB kursi belgilanmagan\n"
        if currency_rates["KZT"] > 0:
            welcome_text += f"{KZT_SIGN} 1{KZT_SIGN} = {currency_rates['KZT']} so'm"
        else:
            welcome_text += f"{KZT_SIGN} KZT kursi belgilanmagan"
        await query.message.reply_text(welcome_text, reply_markup=currency_menu(user.id))
        context.user_data['state'] = 'currency'

    elif query.data == 'currency_set_rate' and user.id == ADMIN_ID:
        await query.message.reply_text("Kursni o'zgartirmoqchi bo'lgan valyutani tanlang:", reply_markup=currency_set_rate_menu())
        context.user_data['state'] = 'currency_set_rate'

    elif query.data.startswith('set_rate_') and user.id == ADMIN_ID:
        currency = query.data.split('_')[-1].upper()
        context.user_data['selected_currency'] = currency
        await query.message.reply_text(f"Yangi {currency} kursini kiriting (1 {currency} = necha so'm):")
        bot_state.waiting_for_rate = True
        context.user_data['state'] = 'currency_set_rate_value'

    elif query.data == 'currency_convert':
        message = "Konvertatsiya turini tanlang. Joriy kurslar:\n"
        if currency_rates["USD"] > 0:
            message += f"💵 1{DOLLAR_SIGN} = {currency_rates['USD']} so'm\n"
        else:
            message += f"💵 USD kursi belgilanmagan\n"
        if currency_rates["RUB"] > 0:
            message += f"{RUB_SIGN} 1{RUB_SIGN} = {currency_rates['RUB']} so'm\n"
        else:
            message += f"{RUB_SIGN} RUB kursi belgilanmagan\n"
        if currency_rates["KZT"] > 0:
            message += f"{KZT_SIGN} 1{KZT_SIGN} = {currency_rates['KZT']} so'm"
        else:
            message += f"{KZT_SIGN} KZT kursi belgilanmagan"
        await query.message.reply_text(message, reply_markup=conversion_menu())
        context.user_data['state'] = 'currency_convert'

    elif query.data == 'currency_dollar_to_sum':
        if currency_rates["USD"] <= 0:
            await query.message.reply_text("USD kursi hali belgilanmagan.")
            return
        await query.message.reply_text("Dollar miqdorini kiriting (faqat son):")
        bot_state.waiting_for_dollar_amount = True
        context.user_data['state'] = 'currency_dollar_to_sum'

    elif query.data == 'currency_sum_to_dollar':
        if currency_rates["USD"] <= 0:
            await query.message.reply_text("USD kursi hali belgilanmagan.")
            return
        await query.message.reply_text("So'm miqdorini kiriting (faqat son):")
        bot_state.waiting_for_sum_to_dollar = True
        context.user_data['state'] = 'currency_sum_to_dollar'

    elif query.data == 'currency_rub_to_sum':
        if currency_rates["RUB"] <= 0:
            await query.message.reply_text("RUB kursi hali belgilanmagan.")
            return
        await query.message.reply_text("Rubl miqdorini kiriting (faqat son):")
        bot_state.waiting_for_rub_amount = True
        context.user_data['state'] = 'currency_rub_to_sum'

    elif query.data == 'currency_sum_to_rub':
        if currency_rates["RUB"] <= 0:
            await query.message.reply_text("RUB kursi hali belgilanmagan.")
            return
        await query.message.reply_text("So'm miqdorini kiriting (faqat son):")
        bot_state.waiting_for_sum_to_rub = True
        context.user_data['state'] = 'currency_sum_to_rub'

    elif query.data == 'currency_kzt_to_sum':
        if currency_rates["KZT"] <= 0:
            await query.message.reply_text("KZT kursi hali belgilanmagan.")
            return
        await query.message.reply_text("Tenge miqdorini kiriting (faqat son):")
        bot_state.waiting_for_kzt_amount = True
        context.user_data['state'] = 'currency_kzt_to_sum'

    elif query.data == 'currency_sum_to_kzt':
        if currency_rates["KZT"] <= 0:
            await query.message.reply_text("KZT kursi hali belgilanmagan.")
            return
        await query.message.reply_text("So'm miqdorini kiriting (faqat son):")
        bot_state.waiting_for_sum_to_kzt = True
        context.user_data['state'] = 'currency_sum_to_kzt'

    elif query.data == 'chat':
        await query.message.reply_text(
            " Aziz Yordamchi chatiga xush kelibsiz!\nSavol yuboring.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Orqaga", callback_data='main')]])
        )
        context.user_data['state'] = 'chat'

    elif query.data == 'aloqa':
        await query.message.reply_text(
            "👨‍💻 Admin bilan bog'lanish: @Azizjon2402\n📞 Telefon: +998 90 714 76 56",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Orqaga", callback_data='main')]])
        )
        context.user_data['state'] = None

    elif query.data == 'weather':
        await query.message.reply_text(
            "🌤️ Ob-havo bo'limi! Viloyatni tanlang:",
            reply_markup=weather_menu()
        )
        context.user_data['state'] = 'weather'

    elif query.data.startswith('weather_') and not query.data.startswith(
            'weather_today_') and not query.data.startswith('weather_tomorrow_') and not query.data.startswith(
            'weather_week_'):
        region = query.data.replace('weather_', '')
        await query.message.reply_text(
            f"{region} uchun ob-havo ma'lumotini tanlang:",
            reply_markup=weather_detail_menu(region)
        )
        context.user_data['state'] = 'weather_detail'

    elif query.data.startswith('weather_today_'):
        region = query.data.replace('weather_today_', '')
        coords = REGIONS.get(region)
        forecast = get_forecast(coords['lat'], coords['lon'])
        if 'error' in forecast:
            await query.message.reply_text(forecast['error'])
            return
        current_date = datetime.now().strftime("%Y-%m-%d")
        end_time = datetime.now().replace(hour=23, minute=59, second=59).strftime("%Y-%m-%d %H:%M:%S")
        message = f"🌤️ {region} - Bugungi ob-havo (hozirgacha kechki 23:59):\n"
        found = False
        for item in forecast['list']:
            if current_date in item['dt_txt'] and item['dt_txt'] <= end_time:
                message += f"🕒 {item['dt_txt'].split(' ')[1]}:\n"
                message += f"🌡️ Harorat: {item['main']['temp']}°C\n"
                message += f"🌬 Shamol: {item['wind']['speed']} m/s\n"
                message += f"💧 Namlik: {item['main']['humidity']}%\n"
                message += f"☁️ Holat: {item['weather'][0]['description']}\n\n"
                found = True
        if not found:
            message += "⚠️ Bugungi ma'lumotlar topilmadi."
        await query.message.reply_text(message, reply_markup=weather_detail_menu(region))

    elif query.data.startswith('weather_tomorrow_'):
        region = query.data.replace('weather_tomorrow_', '')
        coords = REGIONS.get(region)
        forecast = get_forecast(coords['lat'], coords['lon'])
        if 'error' in forecast:
            await query.message.reply_text(forecast['error'])
            return
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        message = f"🌤️ {region} - Ertangi ob-havo:\n"
        for item in forecast['list']:
            if tomorrow in item['dt_txt']:
                message += f"🕒 {item['dt_txt'].split(' ')[1]}:\n"
                message += f"🌡️ Harorat: {item['main']['temp']}°C\n"
                message += f"🌬 Shamol: {item['wind']['speed']} m/s\n"
                message += f"💧 Namlik: {item['main']['humidity']}%\n"
                message += f"☁️ Holat: {item['weather'][0]['description']}\n\n"
        await query.message.reply_text(message, reply_markup=weather_detail_menu(region))

    elif query.data.startswith('weather_week_'):
        region = query.data.replace('weather_week_', '')
        coords = REGIONS.get(region)
        forecast = get_forecast(coords['lat'], coords['lon'])
        if 'error' in forecast:
            await query.message.reply_text(forecast['error'])
            return
        message = f"🌤️ {region} - 7 kunlik prognoz:\n"
        daily = {}
        for item in forecast['list']:
            date = item['dt_txt'].split(' ')[0]
            if date not in daily:
                daily[date] = item
        for date, item in list(daily.items())[:7]:
            message += f"📅 {date}:\n"
            message += f"🌡️ Harorat: {item['main']['temp']}°C\n"
            message += f"☁️ Holat: {item['weather'][0]['description']}\n\n"
        await query.message.reply_text(message, reply_markup=weather_detail_menu(region))

    elif query.data == 'timezone':
        tz = pytz.timezone(TIMEZONES["O'zbekiston"]["tz"])
        time = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
        message = f"🕒 O'zbekiston vaqti: {time}\n\nDavlatni tanlang:"
        await query.message.reply_text(message, reply_markup=timezone_menu())
        context.user_data['state'] = 'timezone'

    elif query.data.startswith('timezone_'):
        country = query.data.replace('timezone_', '')
        tz = pytz.timezone(TIMEZONES[country]['tz'])
        time = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
        message = f"{TIMEZONES[country]['flag']} {country}: {time}"
        await query.message.reply_text(message, reply_markup=timezone_menu())
        context.user_data['state'] = 'timezone'

    elif query.data == 'economics':
        message = "📈 O'zbekiston iqtisodiy statistikasi:\n\n"
        message += "🔍 Mikro iqtisodiyot:\n"
        message += "- Kichik va o'rta biznes: 2024-yilda 56% iqtisodiyot ulushi.\n"
        message += "- Ishsizlik darajasi: ~7.2% (2024-yil).\n\n"
        message += "🌐 Makro iqtisodiyot:\n"
        message += "- YAIM: $90 mlrd (2024-yil, taxminiy).\n"
        message += "- YAM (yillik o'sish): ~5.5% (2024-yil).\n"
        message += "- Inflyatsiya: ~9% (2024-yil).\n"
        message += "- Eksport: $20 mlrd (asosan paxta, oltin, gaz).\n"
        await query.message.reply_text(message, reply_markup=main_menu(user.id))
        context.user_data['state'] = None

    elif query.data == 'survey':
        await query.message.reply_text(
            "📝 Sorovnoma bo'limi!\nTanlang:",
            reply_markup=survey_menu()
        )
        context.user_data['state'] = 'survey'

    elif query.data == 'survey_new':
        await query.message.reply_text(
            "📝 Yangi sorovnoma:\nMavzu kiriting (maks. 50 belgi):",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Orqaga", callback_data='survey')]])
        )
        context.user_data['state'] = 'survey_topic'

    elif query.data == 'survey_results':
        if not surveys_data:
            await query.message.reply_text("📉 Hozircha sorovnomalar yo'q.")
            return
        message = "📊 Sorovnoma natijalari:\n\n"
        for user_id, surveys in surveys_data.items():
            for survey in surveys:
                message += f"👤 @{users_data[user_id]['username']}:\n"
                message += f"📌 Mavzu: {survey['topic']}\n"
                message += f"💭 Fikr: {survey['opinion']}\n"
                message += f"⭐ Baho: {survey['rating']}/5\n"
                message += f"🕒 {survey['timestamp']}\n\n"
        await query.message.reply_text(message, reply_markup=survey_menu())

    elif query.data == 'birthday':
        await query.message.reply_text(
            "🎂 Tug'ilgan kun bo'limi!\nTanlang:",
            reply_markup=birthday_menu()
        )
        context.user_data['state'] = 'birthday'

    elif query.data == 'birthday_set':
        await query.message.reply_text(
            "🎂 Ismingizni kiriting:",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Orqaga", callback_data='birthday')]])
        )
        context.user_data['state'] = 'birthday_name'

    elif query.data == 'birthday_view':
        user_id = str(user.id)
        if user_id not in birthdays_data:
            await query.message.reply_text("⚠️ Tug'ilgan kun ma'lumotlari topilmadi.")
            return
        data = birthdays_data[user_id]
        birth_date = datetime.strptime(data['date'], "%d-%m-%Y")
        today = datetime.now()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        next_birthday = birth_date.replace(year=today.year)
        if next_birthday < today:
            next_birthday = next_birthday.replace(year=today.year + 1)
        days_to_birthday = (next_birthday - today).days
        message = f"🎂 {data['name']}, siz {age} yoshdasiz.\n"
        if days_to_birthday == 0:
            message += "🎉 Tabriklayman, tug'ilgan kuningiz bilan! Umringiz uzoq bo'lsin!"
        else:
            message += f"📅 Keyingi tug'ilgan kuningizga {days_to_birthday} kun qoldi."
        await query.message.reply_text(message, reply_markup=birthday_menu())

    elif query.data == 'rsa':
        await query.message.reply_text(
            "🔒 RSA shifrlash/deshifrlash bo'limi:\nTanlang:",
            reply_markup=rsa_menu()
        )
        context.user_data['state'] = 'rsa'

    elif query.data == 'rsa_encrypt':
        await query.message.reply_text(
            "🔒 Shifrlamoqchi bo'lgan matnni kiriting (maks. 255 belgi):",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Orqaga", callback_data='rsa')]])
        )
        context.user_data['state'] = 'rsa_encrypt_text'

    elif query.data == 'rsa_decrypt':
        await query.message.reply_text(
            "🔓 Yopiq kalitni kiriting (d, n formatida, masalan: 123,456):",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Orqaga", callback_data='rsa')]])
        )
        context.user_data['state'] = 'rsa_decrypt_key'


    elif query.data == 'tarjima':
        await query.message.reply_text(
            "🌐 Tarjima bo'limi!\nTarjima yo'nalishini tanlang:",
            reply_markup=tarjima_menu()
        )
        context.user_data['state'] = 'tarjima'

    elif query.data.startswith('tarjima_'):
        langs = query.data.split('_')[1:]
        source_lang, target_lang = langs[0], langs[1]
        context.user_data['source_lang'] = source_lang
        context.user_data['target_lang'] = target_lang
        await query.message.reply_text(
            f"{FLAGS.get(source_lang)} → {FLAGS.get(target_lang)} tarjima uchun matn yuboring:",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Orqaga", callback_data='tarjima')]])
        )
        context.user_data['state'] = 'tarjima_text'


    elif query.data == 'translit':
        await query.message.reply_text(
            "🔤 Transliteratsiya bo'limi!\nTransliteratsiya turini tanlang:",
            reply_markup=translit_menu()
        )
        context.user_data['state'] = 'translit'

    elif query.data.startswith('translit_'):
        parts = query.data.split('_')
        lang, source_script, target_script = parts[1], parts[2], parts[3]
        context.user_data['translit_lang'] = lang
        context.user_data['source_script'] = source_script
        context.user_data['target_script'] = target_script
        await query.message.reply_text(
            f"{source_script} matni yuboring:",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Orqaga", callback_data='translit')]])
        )
        context.user_data['state'] = 'translit_text'


    elif query.data == 'admin' and user.id == ADMIN_ID:
        await query.message.reply_text("Admin panel:", reply_markup=admin_menu())
        context.user_data['state'] = 'admin'

    elif query.data == 'admin_motivations' and user.id == ADMIN_ID:
        pending = [m for m in motivations_data.get("motivations", []) if m["status"] == "pending"]
        if not pending:
            await query.message.reply_text("Tasdiqlanmagan motivatsiyalar yo'q.", reply_markup=admin_menu())
            return
        for motivation in pending:
            keyboard = [
                [
                    InlineKeyboardButton("✅ Tasdiqlash", callback_data=f"motiv_approve_{motivation['id']}"),
                    InlineKeyboardButton("❌ Bekor qilish", callback_data=f"motiv_reject_{motivation['id']}")
                ],
                [InlineKeyboardButton("✏️ Tahrirlash", callback_data=f"motiv_edit_{motivation['id']}")]
            ]
            await query.message.reply_text(
                f"ID: {motivation['id']}\nMuallif: @{motivation['author_username']}\nSana: {motivation['added_date']}\n\nText: {motivation['text']}",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        context.user_data['state'] = 'admin_motivations'

    elif query.data == 'admin_users' and user.id == ADMIN_ID:
        message = "📋 Foydalanuvchilar ro'yxati:\n\n"
        for user_id, data in users_data.items():
            status = "✅ Faol" if data.get("is_active", True) else "🚫 Bloklangan"
            message += f"ID: {user_id}\nUsername: @{data['username']}\nIsm: {data['first_name']}\nHolat: {status}\n\n"
        await query.message.reply_text(message, reply_markup=admin_menu())

    elif query.data == 'admin_stats' and user.id == ADMIN_ID:
        active_users = sum(1 for data in users_data.values() if data.get("is_active", True))
        blocked_users = sum(1 for data in users_data.values() if not data.get("is_active", True))
        total_messages = sum(len(data.get("messages", [])) for data in users_data.values())
        stats = f"📊 Bot statistikasi:\n\n"
        stats += f"Umumiy foydalanuvchilar: {len(users_data)}\n"
        stats += f"Faol foydalanuvchilar: {active_users}\n"
        stats += f"Bloklangan foydalanuvchilar: {blocked_users}\n"
        stats += f"Umumiy xabarlar: {total_messages}\n"
        stats += f"Motivatsion so'zlar soni: {len(motivations_data.get('motivations', []))}\n"
        stats += f"RSA ma'lumotlari soni: {len(rsa_data)}\n"
        await query.message.reply_text(stats, reply_markup=admin_menu())

    elif query.data == 'admin_delete_user' and user.id == ADMIN_ID:
        await query.message.reply_text("O'chiriladigan foydalanuvchi ID sini kiriting:")
        context.user_data['state'] = 'admin_delete_user'

    elif query.data == 'admin_block_user' and user.id == ADMIN_ID:
        await query.message.reply_text("Bloklanadigan foydalanuvchi ID sini kiriting:")
        context.user_data['state'] = 'admin_block_user'

    elif query.data == 'admin_messages' and user.id == ADMIN_ID:
        await query.message.reply_text("Xabarlarini ko'rmoqchi bo'lgan foydalanuvchi ID sini kiriting:")
        context.user_data['state'] = 'admin_view_messages'

    elif query.data == 'admin_rsa' and user.id == ADMIN_ID:
        if not rsa_data:
            await query.message.reply_text("📉 Hozircha RSA ma'lumotlari yo'q.")
            return
        await query.message.reply_text(
            "🔒 RSA shifrlangan ma'lumotlar ro'yxati:",
            reply_markup=rsa_list_menu(rsa_data, page=1)
        )
        context.user_data['state'] = 'admin_rsa'

    elif query.data.startswith('rsa_page_'):
        page = int(query.data.split('_')[-1])
        await query.message.reply_text(
            f"🔒 RSA ma'lumotlari (sahifa {page}):",
            reply_markup=rsa_list_menu(rsa_data, page=page)
        )

    elif query.data.startswith('rsa_view_'):
        rsa_id = query.data.split('_')[-1]
        rsa_info = rsa_data.get(rsa_id, {})
        message = f"🔒 RSA ma'lumotlari (ID: {rsa_id[:8]}):\n\n"
        message += f"📝 Asl matn: {rsa_info['plaintext']}\n"
        message += f"🔐 Shifrlangan: {rsa_info['ciphertext']}\n"
        message += f"🔑 Ochiq kalit: {rsa_info['public_key']}\n"
        message += f"🔑 Yopiq kalit: {rsa_info['private_key']}\n"
        message += f"🕒 Vaqt: {rsa_info['timestamp']}"
        await query.message.reply_text(
            message,
            reply_markup=rsa_detail_menu(rsa_id, user.id)
        )
        context.user_data['state'] = 'rsa_view'

    elif query.data.startswith('rsa_edit_') and user.id == ADMIN_ID:
        rsa_id = query.data.split('_')[-1]
        context.user_data['edit_rsa_id'] = rsa_id
        await query.message.reply_text(
            "✏️ Yangi asl matnni kiriting (maks. 255 belgi):",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Orqaga", callback_data='admin_rsa')]])
        )
        context.user_data['state'] = 'rsa_edit_text'

    elif query.data.startswith('rsa_delete_') and user.id == ADMIN_ID:
        rsa_id = query.data.split('_')[-1]
        if rsa_id in rsa_data:
            del rsa_data[rsa_id]
            save_rsa_data()
            await query.message.reply_text("✅ RSA ma'lumoti o'chirildi.")
        else:
            await query.message.reply_text("⚠️ RSA ma'lumoti topilmadi.")
        await query.message.reply_text(
            "🔒 RSA shifrlangan ma'lumotlar ro'yxati:",
            reply_markup=rsa_list_menu(rsa_data, page=1)
        )



    elif query.data == 'main':
        welcome_text = "Asosiy menyu:"
        if user.id == ADMIN_ID:
            welcome_text += f"\nHozirgi kurslar:\n"
            welcome_text += f"💵 {currency_rates['USD']} so'm = 1{DOLLAR_SIGN}\n"
            welcome_text += f"{RUB_SIGN} {currency_rates['RUB']} so'm = 1{RUB_SIGN}\n"
            welcome_text += f"{KZT_SIGN} {currency_rates['KZT']} so'm = 1{KZT_SIGN}"
        await query.message.reply_text(welcome_text, reply_markup=main_menu(user.id))
        context.user_data['state'] = None

# Xabarlar ishlovchisi
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    message_text = update.message.text
    update_user_data(user.id, user.username, user.first_name, message_text)
    state = context.user_data.get('state')
    logger.debug(f"Foydalanuvchi xabari: user_id={user.id}, text={message_text}, state={state}")
    
    if state == 'admin_parol_kutish':
        if message_text == "1234" and user.id == ADMIN_ID:
            await update.message.reply_text("Admin panel:", reply_markup=admin_menu())
            context.user_data['state'] = 'admin'
        else:
            await update.message.reply_text("Parol noto'g'ri.")
            context.user_data['state'] = None

    elif state == 'motiv_sub_time':
        try:
            time_text = message_text.strip()
            datetime.strptime(time_text, "%H:%M")
            frequency = context.user_data.get('motiv_frequency')
            subscribe_to_motivation(user.id, frequency, time_text)
            frequency_text = {"daily": "har kuni", "weekly": "har hafta", "monthly": "har oy"}[frequency]
            await update.message.reply_text(
                f"Siz muvaffaqiyatli tarzda {frequency_text} soat {time_text} da motivatsiya olishga obuna bo'ldingiz!",
                reply_markup=motivation_menu(user.id)
            )
            context.user_data['state'] = 'motivatsiya'
        except ValueError:
            await update.message.reply_text(
                "Noto'g'ri vaqt formati. Iltimos, HH:MM formatida kiriting (masalan: 08:00)",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Orqaga", callback_data='motivatsiya')]])
            )

    elif state == 'motiv_add_text':
        motivation_id = add_motivation(message_text, user.id, user.username or user.first_name)
        await update.message.reply_text(
            "Motivatsiyangiz adminga yuborildi. Tasdiqlanganidan so'ng botda paydo bo'ladi.",
            reply_markup=motivation_menu(user.id)
        )
        if user.id != ADMIN_ID:
            keyboard = [
                [
                    InlineKeyboardButton("✅ Tasdiqlash", callback_data=f"motiv_approve_{motivation_id}"),
                    InlineKeyboardButton("❌ Bekor qilish", callback_data=f"motiv_reject_{motivation_id}")
                ]
            ]
            await context.bot.send_message(
                ADMIN_ID,
                f"Yangi motivatsiya qo'shildi!\n\nID: {motivation_id}\nMuallif: @{user.username or user.first_name}\nText: {message_text}",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        context.user_data['state'] = 'motivatsiya'

    elif state == 'motiv_edit_text' and is_admin(user.id):
        motivation_id = context.user_data.get('edit_motiv_id')
        if motivation_id is None:
            await update.message.reply_text(
                "⚠️ Tahrirlash uchun motivatsiya ID si topilmadi.",
                reply_markup=motivation_menu(user.id)
            )
            context.user_data['state'] = 'motivatsiya'
            return
        if edit_motivation(motivation_id, message_text):
            await update.message.reply_text(
                "✅ Motivatsiya muvaffaqiyatli tahrirlandi!",
                reply_markup=motivation_menu(user.id)
            )
        else:
            await update.message.reply_text(
                "⚠️ Motivatsiya topilmadi yoki tahrirlashda xato yuz berdi.",
                reply_markup=motivation_menu(user.id)
            )
        context.user_data['state'] = 'motivatsiya'
        context.user_data.pop('edit_motiv_id', None)

    elif state == 'currency_set_rate_value' and user.id == ADMIN_ID:
        try:
            rate = float(message_text)
            if rate <= 0:
                raise ValueError("Kurs musbat bo'lishi kerak.")
            currency = context.user_data.get('selected_currency')
            currency_rates[currency] = rate
            save_config()
            await update.message.reply_text(
                f"{currency} kursi muvaffaqiyatli yangilandi: 1 {currency} = {rate} so'm",
                reply_markup=currency_menu(user.id)
            )
            bot_state.waiting_for_rate = False
            context.user_data['state'] = 'currency'
        except ValueError:
            await update.message.reply_text(
                "Iltimos, to'g'ri son kiriting (masalan: 12650.50):"
            )

    elif state == 'currency_dollar_to_sum' and bot_state.waiting_for_dollar_amount:
        try:
            amount = float(message_text)
            if amount <= 0:
                raise ValueError("Miqdor musbat bo'lishi kerak.")
            result = amount * currency_rates["USD"]
            await update.message.reply_text(
                f"{format_currency(amount)} {DOLLAR_SIGN} = {format_currency(result)} so'm",
                reply_markup=conversion_menu()
            )
            bot_state.waiting_for_dollar_amount = False
            context.user_data['state'] = 'currency_convert'
        except ValueError:
            await update.message.reply_text(
                "Iltimos, to'g'ri son kiriting (masalan: 100.50):"
            )

    elif state == 'currency_sum_to_dollar' and bot_state.waiting_for_sum_to_dollar:
        try:
            amount = float(message_text)
            if amount <= 0:
                raise ValueError("Miqdor musbat bo'lishi kerak.")
            result = amount / currency_rates["USD"]
            await update.message.reply_text(
                f"{format_currency(amount)} so'm = {format_currency(result)} {DOLLAR_SIGN}",
                reply_markup=conversion_menu()
            )
            bot_state.waiting_for_sum_to_dollar = False
            context.user_data['state'] = 'currency_convert'
        except ValueError:
            await update.message.reply_text(
                "Iltimos, to'g'ri son kiriting (masalan: 1000000):"
            )

    elif state == 'currency_rub_to_sum' and bot_state.waiting_for_rub_amount:
        try:
            amount = float(message_text)
            if amount <= 0:
                raise ValueError("Miqdor musbat bo'lishi kerak.")
            result = amount * currency_rates["RUB"]
            await update.message.reply_text(
                f"{format_currency(amount)} {RUB_SIGN} = {format_currency(result)} so'm",
                reply_markup=conversion_menu()
            )
            bot_state.waiting_for_rub_amount = False
            context.user_data['state'] = 'currency_convert'
        except ValueError:
            await update.message.reply_text(
                "Iltimos, to'g'ri son kiriting (masalan: 5000):"
            )

    elif state == 'currency_sum_to_rub' and bot_state.waiting_for_sum_to_rub:
        try:
            amount = float(message_text)
            if amount <= 0:
                raise ValueError("Miqdor musbat bo'lishi kerak.")
            result = amount / currency_rates["RUB"]
            await update.message.reply_text(
                f"{format_currency(amount)} so'm = {format_currency(result)} {RUB_SIGN}",
                reply_markup=conversion_menu()
            )
            bot_state.waiting_for_sum_to_rub = False
            context.user_data['state'] = 'currency_convert'
        except ValueError:
            await update.message.reply_text(
                "Iltimos, to'g'ri son kiriting (masalan: 1000000):"
            )

    elif state == 'currency_kzt_to_sum' and bot_state.waiting_for_kzt_amount:
        try:
            amount = float(message_text)
            if amount <= 0:
                raise ValueError("Miqdor musbat bo'lishi kerak.")
            result = amount * currency_rates["KZT"]
            await update.message.reply_text(
                f"{format_currency(amount)} {KZT_SIGN} = {format_currency(result)} so'm",
                reply_markup=conversion_menu()
            )
            bot_state.waiting_for_kzt_amount = False
            context.user_data['state'] = 'currency_convert'
        except ValueError:
            await update.message.reply_text(
                "Iltimos, to'g'ri son kiriting (masalan: 5000):"
            )

    elif state == 'currency_sum_to_kzt' and bot_state.waiting_for_sum_to_kzt:
        try:
            amount = float(message_text)
            if amount <= 0:
                raise ValueError("Miqdor musbat bo'lishi kerak.")
            result = amount / currency_rates["KZT"]
            await update.message.reply_text(
                f"{format_currency(amount)} so'm = {format_currency(result)} {KZT_SIGN}",
                reply_markup=conversion_menu()
            )
            bot_state.waiting_for_sum_to_kzt = False
            context.user_data['state'] = 'currency_convert'
        except ValueError:
            await update.message.reply_text(
                "Iltimos, to'g'ri son kiriting (masalan: 1000000):"
            )

    elif state == 'chat':
        response = query_gemini(message_text)
        await update.message.reply_text(
            response,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Orqaga", callback_data='main')]])
        )

    elif state == 'survey_topic':
        if len(message_text) > 50:
            await update.message.reply_text(
                "Mavzu 50 belgidan oshmasligi kerak. Iltimos, qayta kiriting:"
            )
            return
        context.user_data['survey_topic'] = message_text
        await update.message.reply_text(
            "Fikringizni yozing (maks. 200 belgi):",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Orqaga", callback_data='survey')]])
        )
        context.user_data['state'] = 'survey_opinion'

    elif state == 'survey_opinion':
        if len(message_text) > 200:
            await update.message.reply_text(
                "Fikr 200 belgidan oshmasligi kerak. Iltimos, qayta kiriting:"
            )
            return
        context.user_data['survey_opinion'] = message_text
        await update.message.reply_text(
            "Baho bering (1-5):",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Orqaga", callback_data='survey')]])
        )
        context.user_data['state'] = 'survey_rating'

    elif state == 'survey_rating':
        try:
            rating = int(message_text)
            if rating < 1 or rating > 5:
                raise ValueError("Baho 1-5 oralig'ida bo'lishi kerak.")
            user_id = str(user.id)
            if user_id not in surveys_data:
                surveys_data[user_id] = []
            surveys_data[user_id].append({
                'topic': context.user_data['survey_topic'],
                'opinion': context.user_data['survey_opinion'],
                'rating': rating,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            save_surveys()
            await update.message.reply_text(
                "✅ Sorovnoma muvaffaqiyatli saqlandi!",
                reply_markup=survey_menu()
            )
            context.user_data['state'] = 'survey'
        except ValueError:
            await update.message.reply_text(
                "Iltimos, 1-5 oralig'ida son kiriting:"
            )

    elif state == 'birthday_name':
        context.user_data['birthday_name'] = message_text
        await update.message.reply_text(
            "Tug'ilgan kuningizni kiriting (DD-MM-YYYY, masalan: 01-01-2000):",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Orqaga", callback_data='birthday')]])
        )
        context.user_data['state'] = 'birthday_date'

    elif state == 'birthday_date':
        try:
            date = datetime.strptime(message_text, "%d-%m-%Y")
            user_id = str(user.id)
            birthdays_data[user_id] = {
                'name': context.user_data['birthday_name'],
                'date': message_text
            }
            save_birthdays()
            await update.message.reply_text(
                "🎂 Tug'ilgan kun muvaffaqiyatli saqlandi!",
                reply_markup=birthday_menu()
            )
            context.user_data['state'] = 'birthday'
        except ValueError:
            await update.message.reply_text(
                "Noto'g'ri sana formati. Iltimos, DD-MM-YYYY formatida kiriting (masalan: 01-01-2000):"
            )

    elif state == 'rsa_encrypt_text':
        if len(message_text) > 255:
            await update.message.reply_text("Matn 255 belgidan oshmasligi kerak!")
            return
        context.user_data['rsa_plaintext'] = message_text
        await update.message.reply_text(
            "p tub sonini kiriting:",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Orqaga", callback_data='rsa')]])
        )
        context.user_data['state'] = 'rsa_encrypt_p'

    elif state == 'rsa_encrypt_p':
        try:
            p = int(message_text)
            if not is_prime(p):
                await update.message.reply_text("p tub son bo'lishi kerak!")
                return
            context.user_data['rsa_p'] = p
            await update.message.reply_text(
                "q tub sonini kiriting:",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Orqaga", callback_data='rsa')]])
            )
            context.user_data['state'] = 'rsa_encrypt_q'
        except ValueError:
            await update.message.reply_text("Iltimos, to'g'ri son kiriting.")

    elif state == 'rsa_encrypt_q':
        try:
            q = int(message_text)
            if not is_prime(q):
                await update.message.reply_text("q tub son bo'lishi kerak!")
                return
            p = context.user_data['rsa_p']
            plaintext = context.user_data['rsa_plaintext']
            public_key, private_key = generate_keys(p, q)
            cipher = encrypt(public_key, plaintext)
            rsa_id = str(uuid.uuid4())
            rsa_data[rsa_id] = {
                "plaintext": plaintext,
                "ciphertext": ','.join(map(str, cipher)),
                "public_key": public_key,
                "private_key": private_key,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            save_rsa_data()
            message = f"🔒 Shifrlangan ma'lumot:\n"
            message += f"📝 Asl matn: {plaintext}\n"
            message += f"🔐 Shifrlangan: {','.join(map(str, cipher))}\n"
            message += f"🔑 Ochiq kalit: {public_key}\n"
            message += f"🔑 Yopiq kalit: {private_key}\n"
            message += f"🆔 ID: {rsa_id[:8]}"
            await update.message.reply_text(message, reply_markup=rsa_menu())
            context.user_data['state'] = 'rsa'
        except Exception as e:
            await update.message.reply_text(f"Shifrlash xatosi: {str(e)}")

    elif state == 'rsa_decrypt_key':
        try:
            d, n = map(int, message_text.split(','))
            context.user_data['rsa_private_key'] = (d, n)
            await update.message.reply_text(
                "Shifrlangan matnni kiriting (raqamlar, vergul bilan ajratilgan):",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Orqaga", callback_data='rsa')]])
            )
            context.user_data['state'] = 'rsa_decrypt_text'
        except ValueError:
            await update.message.reply_text("Iltimos, to'g'ri formatda kiriting (masalan: 123,456).")

    elif state == 'rsa_decrypt_text':
        try:
            private_key = context.user_data['rsa_private_key']
            decrypted = decrypt(private_key, message_text)
            await update.message.reply_text(
                f"🔓 Deshifrlangan matn:\n{decrypted}",
                reply_markup=rsa_menu()
            )
            context.user_data['state'] = 'rsa'
        except Exception as e:
            await update.message.reply_text(f"Deshifrlash xatosi: {str(e)}")

    elif state == 'rsa_edit_text' and user.id == ADMIN_ID:
        rsa_id = context.user_data.get('edit_rsa_id')
        if rsa_id not in rsa_data:
            await update.message.reply_text("⚠️ RSA ma'lumoti topilmadi.")
            return
        if len(message_text) > 255:
            await update.message.reply_text("Matn 255 belgidan oshmasligi kerak!")
            return
        rsa_data[rsa_id]['plaintext'] = message_text
        p, q = rsa_data[rsa_id]['public_key'][1], rsa_data[rsa_id]['private_key'][1]
        public_key, private_key = generate_keys(p, q)
        cipher = encrypt(public_key, message_text)
        rsa_data[rsa_id]['ciphertext'] = ','.join(map(str, cipher))
        rsa_data[rsa_id]['public_key'] = public_key
        rsa_data[rsa_id]['private_key'] = private_key
        rsa_data[rsa_id]['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        save_rsa_data()
        await update.message.reply_text(
            "✅ RSA ma'lumoti tahrirlandi!",
            reply_markup=rsa_detail_menu(rsa_id, user.id)
        )
        context.user_data['state'] = 'rsa_view'


    elif state == 'tarjima_text':
        source_lang = context.user_data.get('source_lang')
        target_lang = context.user_data.get('target_lang')
        translated = mymemory_translate(message_text, source_lang, target_lang)
        await update.message.reply_text(
            f"🌐 Tarjima:\n\n{translated}",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Orqaga", callback_data='tarjima')]])
        )

    elif state == 'translit_text':
        lang = context.user_data.get('translit_lang')
        source_script = context.user_data.get('source_script')
        target_script = context.user_data.get('target_script')
        result = transliterate(message_text, lang, lang, source_script, target_script)
        await update.message.reply_text(
            f"🔤 Transliteratsiya:\n\n{result}",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Orqaga", callback_data='translit')]])
        )

    elif state == 'admin_delete_user' and user.id == ADMIN_ID:
        user_id = message_text.strip()
        if user_id in users_data:
            del users_data[user_id]
            save_users_data()
            await update.message.reply_text(
                f"✅ Foydalanuvchi (ID: {user_id}) o'chirildi.",
                reply_markup=admin_menu()
            )
        else:
            await update.message.reply_text(
                "⚠️ Foydalanuvchi topilmadi."
            )
        context.user_data['state'] = 'admin'

    elif state == 'admin_block_user' and user.id == ADMIN_ID:
        user_id = message_text.strip()
        if user_id in users_data:
            users_data[user_id]['is_active'] = False
            save_users_data()
            await update.message.reply_text(
                f"🚫 Foydalanuvchi (ID: {user_id}) bloklandi.",
                reply_markup=admin_menu()
            )
        else:
            await update.message.reply_text(
                "⚠️ Foydalanuvchi topilmadi."
            )
        context.user_data['state'] = 'admin'

    elif state == 'admin_view_messages' and user.id == ADMIN_ID:
        user_id = message_text.strip()
        if user_id in users_data:
            messages = users_data[user_id].get('messages', [])
            if not messages:
                await update.message.reply_text(
                    "Bu foydalanuvchidan xabarlar yo'q."
                )
            else:
                message = f"📬 Foydalanuvchi (ID: {user_id}) xabarlari:\n\n"
                for msg in messages:
                    message += f"🕒 {msg['timestamp']}: {msg['text']}\n"
                await update.message.reply_text(
                    message,
                    reply_markup=admin_menu()
                )
        else:
            await update.message.reply_text(
                "⚠️ Foydalanuvchi topilmadi."
            )
        context.user_data['state'] = 'admin'

    else:
        await update.message.reply_text(
            "Iltimos, menyudan funksiyani tanlang:",
            reply_markup=main_menu(user.id)
        )
        context.user_data['state'] = None

# Botni ishga tushirish
def main():
    load_config()
    load_users_data()
    load_surveys()
    load_birthdays()
    load_motivations()
    load_subscriptions()
    load_rsa_data()

    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Buyruqlar
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("aziz", aziz))

    # Tugma callback
    application.add_handler(CallbackQueryHandler(button_callback))

    # Xabarlar ishlovchisi
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    # Rejalashtirilgan motivatsiyalarni yuborish
    application.job_queue.run_once(
        lambda context: asyncio.create_task(send_scheduled_motivations(context)),
        when=0
    )

    logger.info("Bot ishga tushdi!")
    application.run_polling()

if __name__ == '__main__':
    main()
