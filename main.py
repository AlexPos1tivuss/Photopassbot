import logging
import os
from flask import Flask
import telebot
from telebot import types
import requests
import base64
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import io

API_TOKEN = '7663150988:AAEecipedAuXLmZdWhFEJLNlKh25wrD8kRM'
CUTOUT_API_KEY = 'd7ef1252677441b49402f5326ce7712f'
PAYMENT_API_KEY = '401643678:TEST:b6cd3f8b-8967-4916-8b3a-55c70960c07e'

logging.basicConfig(level=logging.INFO)
bot = telebot.TeleBot(API_TOKEN)


current_mode = None  

def main_menu_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(
        types.KeyboardButton('Примеры'),
        types.KeyboardButton('Удаление фона'),
        types.KeyboardButton('Инструкция как фоткаться'),
        types.KeyboardButton('Фото на паспорт визу')
    )
    return keyboard

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, 'Привет! Я ваш бот для фото услуг.\n Умный бот 🤖 поможет сделать, красивое фото на паспорт, прямо дома 🥰', reply_markup=main_menu_keyboard())

@bot.message_handler(func=lambda message: message.text == 'Примеры')
def send_examples(message):
    try:
        photos = []
        for photo_file in os.listdir('images'):
            if photo_file.endswith('.jpg'):
                with open(os.path.join('images', photo_file), 'rb') as photo:
                    photos.append(photo.read())
        if photos:
            media_group = [types.InputMediaPhoto(photo) for photo in photos]
            bot.send_media_group(message.chat.id, media_group)
        else:
            bot.send_message(message.chat.id, 'Примеры отсутствуют.')
    except Exception as e:
        logging.error(f"Ошибка при отправке примеров: {e}")
        bot.send_message(message.chat.id, f"Произошла ошибка при загрузке примеров. {e}")

@bot.message_handler(func=lambda message: message.text == 'Инструкция как фоткаться')
def send_instruction(message):
    instruction_text = '''
    ПАМЯТКА ПО ИСХОДНОЙ ФОТОГРАФИИ 🤳 
        Фото анфас: лицо, шея, плечи четко прямо
        Нейтральное выражение лица, отсутствие широкой улыбки/угрюмости
        Глаза открыты, без цветных линз
        Взгляд направлен прямо в объектив
        Фото без масок и фильтров
        Без головных уборов темных очков
        Хороший свет: лучше напротив источника света
    '''
    with open('photo_2024-10-11_12-09-00.jpg', 'rb') as photo:
        bot.send_photo(message.chat.id, photo, caption=instruction_text)


@bot.message_handler(func=lambda message: message.text == 'Удаление фона')
def background_removal(message):
    global current_mode
    current_mode = 'Удаление фона'
    bot.send_message(message.chat.id, 'Пожалуйста, пришлите фото для удаления фона или нажмите "Отмена".', reply_markup=cancel_keyboard())

@bot.message_handler(func=lambda message: message.text == 'Фото на паспорт визу')
def send_photo_type_options(message):
    global current_mode
    photo_type_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    photo_type_keyboard.add(
        types.KeyboardButton('Паспорт'),
        types.KeyboardButton('Виза'),
        types.KeyboardButton('Отмена')
    )
    bot.send_message(message.chat.id, 'Выберите тип фото:', reply_markup=photo_type_keyboard)

    @bot.message_handler(func=lambda message: message.text in ['Паспорт', 'Виза'])
    def handle_photo_type_selection(message):
        global current_mode
        if message.text == 'Паспорт':
            current_mode = 'Паспорт'
            send_country_options(message)
        elif message.text == 'Виза':
            current_mode = 'Виза'
            send_country_options(message)

def send_country_options(message):
    country_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    countries = [
        '🇧🇾 Беларусь', '🇷🇺 Россия', '🇰🇿 Казахстан', '🇺🇦 Украина', '🇦🇺 Австралия', '🇦🇿 Азербайджан', '🇦🇱 Албания', '🇩🇿 Алжир', '🇦🇷 Аргентина', '🇧🇩 Бангладеш', '🇧🇧 Барбадос',
        '🇧🇪 Бельгия', '🇧🇿 Белиз', '🇧🇬 Болгария', '🇧🇴 Боливия', '🇧🇷 Бразилия', '🇬🇷 Греция', '🇭🇰 Гонконг', '🇬🇪 Грузия',
        '🇩🇪 Германия', '🇩🇰 Дания', '🇪🇸 Испания', '🇦🇺 Австралия', '🇪🇺 Европейский Союз', '🇪🇪 Эстония', '🇰🇵 Северная Корея',
        '🇰🇷 Южная Корея', '🇮🇱 Израиль', '🇮🇳 Индия', '🇮🇩 Индонезия', '🇯🇲 Ямайка', '🇯🇵 Япония', '🇮🇶 Ирак', '🇮🇹 Италия',
        '🇨🇦 Канада', '🇰🇭 Камбоджа', '🇶🇦 Катар', '🇴🇲 Оман', '🇰🇪 Кения', '🇨🇳 Китай',
        '🇰🇬 Кыргызстан', '🇱🇧 Ливан', '🇲🇾 Малайзия', '🇲🇽 Мексика', '🇩🇿 Марокко',
        '🇳🇿 Новая Зеландия', '🇳🇬 Нигерия', '🇳🇱 Нидерланды', '🇳🇴 Норвегия', '🇵🇰 Пакистан',
        '🇵🇦 Панама', '🇵🇷 Перу', '🇵🇹 Португалия', '🇷🇴 Румыния', '🇸🇬 Сингапур',
        '🇪🇸 Испания', '🇰🇿 Казахстан', '🇿🇦 Южная Африка', '🇸🇾 Сирия', '🇹🇭 Таиланд',
        '🇹🇯 Таджикистан', '🇹🇹 Тринидад и Тобаго', '🇹🇷 Турция', '🇦🇪 Объединенные Арабские Эмираты',
        '🇺🇿 Узбекистан', '🇺🇸 Соединенные Штаты', '🇫🇷 Франция', '🇫🇮 Финляндия',
        '🇪🇸 Испания', '🇹🇼 Тайвань', '🇹🇿 Танзания', '🇵🇪 Перу', '🇵🇹 Португалия',
        '🇭🇺 Венгрия', '🇯🇴 Иордания', '🇦🇩 Андорра', '🇪🇺 ЕС', '🇵🇭 Филиппины',
        '🇵🇱 Польша', '🇹🇯 Таджикистан', '🇹🇷 Турция', '🇺🇸 США',
        '🇺🇾 Уругвай', '🇻🇪 Венесуэла', '🇻🇳 Вьетнам', '🇮🇪 Ирландия', '🇿🇼 Зимбабве',
        '🇰🇼 Кувейт', '🇹🇭 Таиланд', '🇵🇦 Панама',
        '🇫🇯 Фиджи', '🇬🇧 Великобритания', '🇨🇭 Швейцария', '🇰🇷 Южная Корея', '🇲🇦 Марокко', '🇮🇷 Иран', '🇿🇦 Южная Африка',
        '🇯🇲 Ямайка', '🇲🇰 Македония', '🇲🇿 Мозамбик', 'Отмена'
    ]
    for country in countries:
        country_keyboard.add(types.KeyboardButton(country))
    bot.send_message(message.chat.id, 'Выберите страну:', reply_markup=country_keyboard)

byte_im = None

@bot.message_handler(func=lambda message: message.text in [
    '🇦🇺 Австралия', '🇦🇿 Азербайджан', '🇦🇱 Албания', '🇩🇿 Алжир', '🇦🇷 Аргентина', '🇧🇩 Бангладеш', '🇧🇧 Барбадос', '🇧🇾 Беларусь',
    '🇧🇪 Бельгия', '🇧🇿 Белиз', '🇧🇬 Болгария', '🇧🇴 Боливия', '🇧🇷 Бразилия', '🇬🇷 Греция', '🇭🇰 Гонконг', '🇬🇪 Грузия',
    '🇩🇪 Германия', '🇩🇰 Дания', '🇪🇸 Испания', '🇪🇺 Европейский Союз', '🇪🇪 Эстония', '🇰🇵 Северная Корея', '🇰🇷 Южная Корея',
    '🇮🇱 Израиль', '🇮🇳 Индия', '🇮🇩 Индонезия', '🇯🇲 Ямайка', '🇯🇵 Япония', '🇮🇶 Ирак', '🇮🇹 Италия',
    '🇰🇿 Казахстан', '🇨🇦 Канада', '🇰🇭 Камбоджа', '🇶🇦 Катар', '🇴🇲 Оман', '🇰🇪 Кения', '🇨🇳 Китай',
    '🇰🇬 Кыргызстан', '🇱🇧 Ливан', '🇲🇾 Малайзия', '🇲🇽 Мексика', '🇩🇿 Марокко',
    '🇳🇿 Новая Зеландия', '🇳🇬 Нигерия', '🇳🇱 Нидерланды', '🇳🇴 Норвегия', '🇵🇰 Пакистан',
    '🇵🇦 Панама', '🇵🇷 Перу', '🇵🇹 Португалия', '🇷🇴 Румыния', '🇸🇬 Сингапур',
    '🇪🇸 Испания', '🇰🇿 Казахстан', '🇿🇦 Южная Африка', '🇸🇾 Сирия', '🇹🇭 Таиланд',
    '🇹🇯 Таджикистан', '🇹🇹 Тринидад и Тобаго', '🇹🇷 Турция', '🇦🇪 Объединенные Арабские Эмираты',
    '🇺🇿 Узбекистан', '🇺🇸 Соединенные Штаты', '🇫🇷 Франция', '🇫🇮 Финляндия',
    '🇪🇸 Испания', '🇹🇼 Тайвань', '🇹🇿 Танзания', '🇵🇪 Перу', '🇵🇹 Португалия',
    '🇭🇺 Венгрия', '🇯🇴 Иордания', '🇦🇩 Андорра', '🇪🇺 ЕС', '🇵🇭 Филиппины',
    '🇵🇱 Польша', '🇷🇺 Россия', '🇹🇯 Таджикистан', '🇹🇷 Турция', '🇺🇸 США',
    '🇺🇦 Украина', '🇺🇾 Уругвай', '🇻🇪 Венесуэла', '🇻🇳 Вьетнам', '🇮🇪 Ирландия', '🇿🇼 Зимбабве',
    '🇰🇼 Кувейт', '🇹🇭 Таиланд', '🇵🇦 Панама',
    '🇫🇯 Фиджи', '🇬🇧 Великобритания', '🇨🇭 Швейцария', '🇰🇷 Южная Корея', '🇲🇦 Марокко', '🇮🇷 Иран', '🇿🇦 Южная Африка',
    '🇯🇲 Ямайка', '🇲🇰 Македония', '🇲🇿 Мозамбик'])
def request_photo(message):
    global current_mode, selected_country
    selected_country = message.text
    bot.send_message(message.chat.id, 'Пришлите фото для оформления.')

def calculate_print_size(mmHeight, mmWidth):
    photo_count_per_row = 3
    photo_count_per_column = 2

    total_print_width = mmWidth * photo_count_per_row
    total_print_height = mmHeight * photo_count_per_column

    return total_print_height, total_print_width


@bot.message_handler(content_types=['photo'])
def photo_buy(message):
    global current_mode
    bot.send_message(message.chat.id, "Оплатите, чтобы получить фото.")
    if current_mode == 'Удаление фона':
        bot.send_invoice(
            message.chat.id,
            title="Оплата за обработку фото",
            description="Обработка фото",
            provider_token=PAYMENT_API_KEY,
            currency="RUB",
            prices=[types.LabeledPrice(label="Фото без фона", amount=10000)], 
            start_parameter="passport_photo_payment",
            invoice_payload="passport_photo_payload"
        )
    else:
        bot.send_invoice(
            message.chat.id,
            title="Оплата за обработку фото",
            description="Обработка фото",
            provider_token=PAYMENT_API_KEY,
            currency="RUB",
            prices=[types.LabeledPrice(label="Фото на паспорт/виза", amount=30000)], 
            start_parameter="passport_photo_payment",
            invoice_payload="passport_photo_payload"
        )

@bot.pre_checkout_query_handler(func=lambda _: True)
def checkout(query):
    bot.answer_pre_checkout_query(query.id, ok=True)

@bot.message_handler(content_types=['successful_payment'])
def handle_photo(message):
    global current_mode, selected_country, byte_im
    logging.info(f"Платеж успешен: {message.successful_payment.total_amount / 100} {message.successful_payment.currency}")

    if current_mode == 'Удаление фона':
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        response = requests.post(
            'https://www.cutout.pro/api/v1/matting?mattingType=6&outputFormat=png',
            files={'file': downloaded_file},
            headers={'APIKEY': CUTOUT_API_KEY},
        )
        bot.send_document(message.chat.id, io.BytesIO(response.content), caption="Ваше фото с удаленным фоном.", visible_file_name="foto.png")
        bot.send_message(message.chat.id, 'Операция завершена.', reply_markup=main_menu_keyboard())

    elif current_mode == 'Паспорт':
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        image_base64 = base64.b64encode(downloaded_file).decode('utf-8')
        country_settings = {
            '🇧🇾 Беларусь': {'mmHeight': 35, 'mmWidth': 25},
            '🇷🇺 Россия': {'mmHeight': 45, 'mmWidth': 35},
            '🇰🇿 Казахстан': {'mmHeight': 45, 'mmWidth': 35},
            '🇺🇦 Украина': {'mmHeight': 35, 'mmWidth': 25},
            '🇺🇸 США': {'mmHeight': 51, 'mmWidth': 51},
            '🇨🇦 Канада': {'mmHeight': 70, 'mmWidth': 50},
            '🇦🇺 Австралия': {'mmHeight': 45, 'mmWidth': 35},
            '🇦🇿 Азербайджан': {'mmHeight': 50, 'mmWidth': 40},
            '🇦🇱 Албания': {'mmHeight': 50, 'mmWidth': 40},
            '🇩🇿 Алжир': {'mmHeight': 45, 'mmWidth': 35},
            '🇦🇷 Аргентина': {'mmHeight': 45, 'mmWidth': 40},
            '🇧🇩 Бангладеш': {'mmHeight': 45, 'mmWidth': 35},
            '🇧🇧 Барбадос': {'mmHeight': 50, 'mmWidth': 40},
            '🇧🇪 Бельгия': {'mmHeight': 45, 'mmWidth': 35},
            '🇧🇿 Белиз': {'mmHeight': 45, 'mmWidth': 35},
            '🇧🇬 Болгария': {'mmHeight': 45, 'mmWidth': 35},
            '🇧🇴 Боливия': {'mmHeight': 45, 'mmWidth': 40},
            '🇧🇷 Бразилия': {'mmHeight': 70, 'mmWidth': 50},
            '🇬🇷 Греция': {'mmHeight': 50, 'mmWidth': 40},
            '🇭🇰 Гонконг': {'mmHeight': 50, 'mmWidth': 40},
            '🇬🇪 Грузия': {'mmHeight': 50, 'mmWidth': 40},
            '🇩🇪 Германия': {'mmHeight': 45, 'mmWidth': 35},
            '🇩🇰 Дания': {'mmHeight': 45, 'mmWidth': 35},
            '🇪🇸 Испания': {'mmHeight': 50, 'mmWidth': 40},
            '🇪🇺 Европейский Союз': {'mmHeight': 45, 'mmWidth': 35},
            '🇪🇪 Эстония': {'mmHeight': 50, 'mmWidth': 40},
            '🇰🇵 Северная Корея': {'mmHeight': 45, 'mmWidth': 35},
            '🇰🇷 Южная Корея': {'mmHeight': 50, 'mmWidth': 40},
            '🇮🇱 Израиль': {'mmHeight': 55, 'mmWidth': 45},
            '🇮🇳 Индия': {'mmHeight': 50, 'mmWidth': 50},
            '🇮🇩 Индонезия': {'mmHeight': 60, 'mmWidth': 40},
            '🇯🇲 Ямайка': {'mmHeight': 70, 'mmWidth': 50},
            '🇯🇵 Япония': {'mmHeight': 45, 'mmWidth': 35},
            '🇮🇶 Ирак': {'mmHeight': 45, 'mmWidth': 35},
            '🇮🇹 Италия': {'mmHeight': 50, 'mmWidth': 40},
            '🇨🇦 Канада': {'mmHeight': 70, 'mmWidth': 50},
            '🇰🇭 Камбоджа': {'mmHeight': 60, 'mmWidth': 40},
            '🇶🇦 Катар': {'mmHeight': 60, 'mmWidth': 40},
            '🇴🇲 Оман': {'mmHeight': 60, 'mmWidth': 40},
            '🇰🇪 Кения': {'mmHeight': 45, 'mmWidth': 35},
            '🇨🇳 Китай': {'mmHeight': 48, 'mmWidth': 33},
            '🇰🇬 Кыргызстан': {'mmHeight': 45, 'mmWidth': 35},
            '🇱🇧 Ливан': {'mmHeight': 50, 'mmWidth': 40},
            '🇲🇾 Малайзия': {'mmHeight': 50, 'mmWidth': 40},
            '🇲🇽 Мексика': {'mmHeight': 50, 'mmWidth': 40},
            '🇩🇿 Марокко': {'mmHeight': 45, 'mmWidth': 35},
            '🇳🇿 Новая Зеландия': {'mmHeight': 45, 'mmWidth': 35},
            '🇳🇬 Нигерия': {'mmHeight': 45, 'mmWidth': 35},
            '🇳🇱 Нидерланды': {'mmHeight': 45, 'mmWidth': 35},
            '🇳🇴 Норвегия': {'mmHeight': 45, 'mmWidth': 35},
            '🇵🇰 Пакистан': {'mmHeight': 45, 'mmWidth': 35},
            '🇵🇦 Панама': {'mmHeight': 50, 'mmWidth': 40},
            '🇵🇷 Перу': {'mmHeight': 50, 'mmWidth': 40},
            '🇵🇹 Португалия': {'mmHeight': 50, 'mmWidth': 40},
            '🇷🇴 Румыния': {'mmHeight': 50, 'mmWidth': 40},
            '🇸🇬 Сингапур': {'mmHeight': 45, 'mmWidth': 35},
            '🇿🇦 Южная Африка': {'mmHeight': 55, 'mmWidth': 40},
            '🇸🇾 Сирия': {'mmHeight': 50, 'mmWidth': 40},
            '🇹🇭 Таиланд': {'mmHeight': 60, 'mmWidth': 40},
            '🇹🇯 Таджикистан': {'mmHeight': 50, 'mmWidth': 40},
            '🇹🇹 Тринидад и Тобаго': {'mmHeight': 70, 'mmWidth': 50},
            '🇹🇷 Турция': {'mmHeight': 50, 'mmWidth': 40},
            '🇦🇪 Объединенные Арабские Эмираты': {'mmHeight': 50, 'mmWidth': 40},
            '🇺🇿 Узбекистан': {'mmHeight': 45, 'mmWidth': 35},
            '🇫🇷 Франция': {'mmHeight': 45, 'mmWidth': 35},
            '🇫🇮 Финляндия': {'mmHeight': 47, 'mmWidth': 36},
            '🇹🇼 Тайвань': {'mmHeight': 45, 'mmWidth': 35},
            '🇹🇿 Танзания': {'mmHeight': 40, 'mmWidth': 40},
            '🇵🇪 Перу': {'mmHeight': 50, 'mmWidth': 40},
            '🇵🇹 Португалия': {'mmHeight': 50, 'mmWidth': 40},
            '🇭🇺 Венгрия': {'mmHeight': 50, 'mmWidth': 40},
            '🇯🇴 Иордания': {'mmHeight': 45, 'mmWidth': 35},
            '🇦🇩 Андорра': {'mmHeight': 45, 'mmWidth': 35},
            '🇪🇺 ЕС': {'mmHeight': 45, 'mmWidth': 35},
            '🇵🇭 Филиппины': {'mmHeight': 50, 'mmWidth': 35},
            '🇵🇱 Польша': {'mmHeight': 45, 'mmWidth': 35},
            '🇺🇾 Уругвай': {'mmHeight': 45, 'mmWidth': 35},
            '🇻🇪 Венесуэла': {'mmHeight': 50, 'mmWidth': 40},
            '🇻🇳 Вьетнам': {'mmHeight': 60, 'mmWidth': 40},
            '🇮🇪 Ирландия': {'mmHeight': 45, 'mmWidth': 35},
            '🇿🇼 Зимбабве': {'mmHeight': 60, 'mmWidth': 40},
            '🇰🇼 Кувейт': {'mmHeight': 50, 'mmWidth': 40},
            '🇫🇯 Фиджи': {'mmHeight': 50, 'mmWidth': 50},
            '🇬🇧 Великобритания': {'mmHeight': 45, 'mmWidth': 35},
            '🇨🇭 Швейцария': {'mmHeight': 45, 'mmWidth': 35},
            '🇲🇦 Марокко': {'mmHeight': 45, 'mmWidth': 35},
            '🇮🇷 Иран': {'mmHeight': 45, 'mmWidth': 35},
            '🇯🇲 Ямайка': {'mmHeight': 45, 'mmWidth': 35},
            '🇲🇰 Македония': {'mmHeight': 45, 'mmWidth': 35},
            '🇲🇿 Мозамбик': {'mmHeight': 45, 'mmWidth': 35}
        }
        settings = country_settings.get(selected_country, {'mmHeight': 35, 'mmWidth': 25})
        print_height, print_width = calculate_print_size(settings['mmHeight'], settings['mmWidth'])
        data = {
            "base64": image_base64,
            "bgColor": "FFFFFF",
            "dpi": 300,
            "mmHeight": settings['mmHeight'],
            "mmWidth": settings['mmWidth'],
            "printBgColor": "FFFFFF",
            "printMmHeight": print_width,
            "printMmWidth": print_height
        }

        response = requests.post('https://www.cutout.pro/api/v1/idphoto/printLayout', headers={'APIKEY': CUTOUT_API_KEY, "Content-type": "application/json"}, json=data)

        if response.status_code == 200:
            result_data = response.json()
            layout_url = result_data.get('data', {}).get('printLayoutImage')

            if layout_url:
                image_response = requests.get(layout_url)

                
                qr_image = Image.open('qr.png')
                passport_photo = Image.open(io.BytesIO(image_response.content))

                
                qr_image = qr_image.resize((int(qr_image.width * 1), int(qr_image.height * 1)))

                
                new_width = passport_photo.width  
                new_height = passport_photo.height + qr_image.height + 100  

                
                final_image = Image.new('RGB', (new_width, new_height), (255, 255, 255))

                
                final_image.paste(passport_photo, (0, 0))

                
                qr_position = (20, passport_photo.height)  
                final_image.paste(qr_image, qr_position)

                
                draw = ImageDraw.Draw(final_image)
                try:
                    font = ImageFont.truetype("DejaVuSans.ttf", 30)  
                except IOError:
                    font = ImageFont.load_default()  

                
                text = "ТВОЕ ИДЕАЛЬНОЕ \nФОТО - НАШ ФОРМАТ"
                text_bbox = draw.textbbox((0, 0), text, font=font)
                text_width = text_bbox[2] - text_bbox[0]
                text_height = text_bbox[3] - text_bbox[1]
                text_position = (qr_position[0] + qr_image.width + 20, qr_position[1] + (qr_image.height - text_height) // 2)  

                
                draw.text(text_position, text, (0, 0, 0), font=font)

                
                buf = io.BytesIO()
                final_image.save(buf, format='PNG')
                byte_im = buf.getvalue()
                
                bot.send_document(message.chat.id, byte_im, caption="Спасибо за покупку! Вот ваше фото.", visible_file_name="ВашеФото.jpg")
            else:
                bot.send_message(message.chat.id, "Ошибка: не удалось получить URL фото.")
                logging.error("API не вернул printLayoutImage.")
        else:
            bot.send_message(message.chat.id, f"Ошибка при обработке фото: {response.status_code}")
            logging.error(f"Ошибка API: {response.status_code}, {response.text}")

        bot.send_message(message.chat.id, 'Операция завершена.', reply_markup=main_menu_keyboard())
        
    elif current_mode == 'Виза':
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        image_base64 = base64.b64encode(downloaded_file).decode('utf-8')
        country_settings = {
            '🇧🇾 Беларусь': {'mmHeight': 40, 'mmWidth': 30},
            '🇷🇺 Россия': {'mmHeight': 50, 'mmWidth': 40},
            '🇰🇿 Казахстан': {'mmHeight': 50, 'mmWidth': 40},
            '🇺🇦 Украина': {'mmHeight': 40, 'mmWidth': 30},
            '🇺🇸 США': {'mmHeight': 60, 'mmWidth': 60},
            '🇨🇦 Канада': {'mmHeight': 75, 'mmWidth': 55},
            '🇦🇺 Австралия': {'mmHeight': 50, 'mmWidth': 40},
            '🇦🇿 Азербайджан': {'mmHeight': 55, 'mmWidth': 45},
            '🇦🇱 Албания': {'mmHeight': 55, 'mmWidth': 45},
            '🇩🇿 Алжир': {'mmHeight': 50, 'mmWidth': 40},
            '🇦🇷 Аргентина': {'mmHeight': 50, 'mmWidth': 45},
            '🇧🇩 Бангладеш': {'mmHeight': 50, 'mmWidth': 40},
            '🇧🇧 Барбадос': {'mmHeight': 55, 'mmWidth': 45},
            '🇧🇪 Бельгия': {'mmHeight': 50, 'mmWidth': 40},
            '🇧🇿 Белиз': {'mmHeight': 50, 'mmWidth': 40},
            '🇧🇬 Болгария': {'mmHeight': 50, 'mmWidth': 40},
            '🇧🇴 Боливия': {'mmHeight': 50, 'mmWidth': 45},
            '🇧🇷 Бразилия': {'mmHeight': 75, 'mmWidth': 55},
            '🇬🇷 Греция': {'mmHeight': 55, 'mmWidth': 45},
            '🇭🇰 Гонконг': {'mmHeight': 55, 'mmWidth': 45},
            '🇬🇪 Грузия': {'mmHeight': 55, 'mmWidth': 45},
            '🇩🇪 Германия': {'mmHeight': 50, 'mmWidth': 40},
            '🇩🇰 Дания': {'mmHeight': 50, 'mmWidth': 40},
            '🇪🇸 Испания': {'mmHeight': 55, 'mmWidth': 45},
            '🇪🇺 Европейский Союз': {'mmHeight': 50, 'mmWidth': 40},
            '🇪🇪 Эстония': {'mmHeight': 55, 'mmWidth': 45},
            '🇰🇵 Северная Корея': {'mmHeight': 50, 'mmWidth': 40},
            '🇰🇷 Южная Корея': {'mmHeight': 55, 'mmWidth': 45},
            '🇮🇱 Израиль': {'mmHeight': 60, 'mmWidth': 50},
            '🇮🇳 Индия': {'mmHeight': 55, 'mmWidth': 55},
            '🇮🇩 Индонезия': {'mmHeight': 65, 'mmWidth': 45},
            '🇯🇲 Ямайка': {'mmHeight': 75, 'mmWidth': 55},
            '🇯🇵 Япония': {'mmHeight': 50, 'mmWidth': 40},
            '🇮🇶 Ирак': {'mmHeight': 50, 'mmWidth': 40},
            '🇮🇹 Италия': {'mmHeight': 55, 'mmWidth': 45},
            '🇨🇦 Канада': {'mmHeight': 75, 'mmWidth': 55},
            '🇰🇭 Камбоджа': {'mmHeight': 65, 'mmWidth': 45},
            '🇶🇦 Катар': {'mmHeight': 65, 'mmWidth': 45},
            '🇴🇲 Оман': {'mmHeight': 65, 'mmWidth': 45},
            '🇰🇪 Кения': {'mmHeight': 50, 'mmWidth': 40},
            '🇨🇳 Китай': {'mmHeight': 53, 'mmWidth': 38},
            '🇰🇬 Кыргызстан': {'mmHeight': 50, 'mmWidth': 40},
            '🇱🇧 Ливан': {'mmHeight': 55, 'mmWidth': 45},
            '🇲🇾 Малайзия': {'mmHeight': 55, 'mmWidth': 45},
            '🇲🇽 Мексика': {'mmHeight': 55, 'mmWidth': 45},
            '🇩🇿 Марокко': {'mmHeight': 50, 'mmWidth': 40},
            '🇳🇿 Новая Зеландия': {'mmHeight': 50, 'mmWidth': 40},
            '🇳🇬 Нигерия': {'mmHeight': 50, 'mmWidth': 40},
            '🇳🇱 Нидерланды': {'mmHeight': 50, 'mmWidth': 40},
            '🇳🇴 Норвегия': {'mmHeight': 50, 'mmWidth': 40},
            '🇵🇰 Пакистан': {'mmHeight': 50, 'mmWidth': 40},
            '🇵🇦 Панама': {'mmHeight': 55, 'mmWidth': 45},
            '🇵🇷 Перу': {'mmHeight': 55, 'mmWidth': 45},
            '🇵🇹 Португалия': {'mmHeight': 55, 'mmWidth': 45},
            '🇷🇴 Румыния': {'mmHeight': 55, 'mmWidth': 45},
            '🇸🇬 Сингапур': {'mmHeight': 50, 'mmWidth': 40},
            '🇿🇦 Южная Африка': {'mmHeight': 60, 'mmWidth': 45},
            '🇸🇾 Сирия': {'mmHeight': 55, 'mmWidth': 45},
            '🇹🇭 Таиланд': {'mmHeight': 65, 'mmWidth': 45},
            '🇹🇯 Таджикистан': {'mmHeight': 55, 'mmWidth': 45},
            '🇹🇹 Тринидад и Тобаго': {'mmHeight': 75, 'mmWidth': 55},
            '🇹🇷 Турция': {'mmHeight': 55, 'mmWidth': 45},
            '🇦🇪 Объединенные Арабские Эмираты': {'mmHeight': 55, 'mmWidth': 45},
            '🇺🇿 Узбекистан': {'mmHeight': 50, 'mmWidth': 40},
            '🇫🇷 Франция': {'mmHeight': 50, 'mmWidth': 40},
            '🇫🇮 Финляндия': {'mmHeight': 52, 'mmWidth': 41},
            '🇹🇼 Тайвань': {'mmHeight': 50, 'mmWidth': 40},
            '🇹🇿 Танзания': {'mmHeight': 45, 'mmWidth': 45},
            '🇵🇪 Перу': {'mmHeight': 55, 'mmWidth': 45},
            '🇵🇹 Португалия': {'mmHeight': 55, 'mmWidth': 45},
            '🇭🇺 Венгрия': {'mmHeight': 55, 'mmWidth': 45},
            '🇯🇴 Иордания': {'mmHeight': 50, 'mmWidth': 40},
            '🇦🇩 Андорра': {'mmHeight': 50, 'mmWidth': 40},
            '🇪🇺 ЕС': {'mmHeight': 50, 'mmWidth': 40},
            '🇵🇭 Филиппины': {'mmHeight': 55, 'mmWidth': 40},
            '🇵🇱 Польша': {'mmHeight': 50, 'mmWidth': 40},
            '🇺🇾 Уругвай': {'mmHeight': 50, 'mmWidth': 40},
            '🇻🇪 Венесуэла': {'mmHeight': 55, 'mmWidth': 45},
            '🇻🇳 Вьетнам': {'mmHeight': 65, 'mmWidth': 45},
            '🇮🇪 Ирландия': {'mmHeight': 50, 'mmWidth': 40},
            '🇿🇼 Зимбабве': {'mmHeight': 65, 'mmWidth': 45},
            '🇰🇼 Кувейт': {'mmHeight': 55, 'mmWidth': 45},
            '🇫🇯 Фиджи': {'mmHeight': 55, 'mmWidth': 55},
            '🇬🇧 Великобритания': {'mmHeight': 50, 'mmWidth': 40},
            '🇨🇭 Швейцария': {'mmHeight': 50, 'mmWidth': 40},
            '🇲🇦 Марокко': {'mmHeight': 50, 'mmWidth': 40},
            '🇮🇷 Иран': {'mmHeight': 50, 'mmWidth': 40},
            '🇯🇲 Ямайка': {'mmHeight': 50, 'mmWidth': 40},
            '🇲🇰 Македония': {'mmHeight': 50, 'mmWidth': 40},
            '🇲🇿 Мозамбик': {'mmHeight': 50, 'mmWidth': 40}
        }
        settings = country_settings.get(selected_country, {'mmHeight': 35, 'mmWidth': 25})
        print_height, print_width = calculate_print_size(settings['mmHeight'], settings['mmWidth'])
        data = {
            "base64": image_base64,
            "bgColor": "FFFFFF",
            "dpi": 300,
            "mmHeight": settings['mmHeight'],
            "mmWidth": settings['mmWidth'],
            "printBgColor": "FFFFFF",
            "printMmHeight": print_width,
            "printMmWidth": print_height
        }
    
        response = requests.post('https://www.cutout.pro/api/v1/idphoto/printLayout', headers={'APIKEY': CUTOUT_API_KEY, "Content-type": "application/json"}, json=data)
    
        if response.status_code == 200:
            result_data = response.json()
            layout_url = result_data.get('data', {}).get('printLayoutImage')
    
            if layout_url:
                image_response = requests.get(layout_url)


                qr_image = Image.open('qr.png')
                passport_photo = Image.open(io.BytesIO(image_response.content))


                qr_image = qr_image.resize((int(qr_image.width * 1), int(qr_image.height * 1)))


                new_width = passport_photo.width  
                new_height = passport_photo.height + qr_image.height + 100  


                final_image = Image.new('RGB', (new_width, new_height), (255, 255, 255))


                final_image.paste(passport_photo, (0, 0))


                qr_position = (20, passport_photo.height)  
                final_image.paste(qr_image, qr_position)


                draw = ImageDraw.Draw(final_image)
                try:
                    font = ImageFont.truetype("DejaVuSans.ttf", 40)  
                except IOError:
                    font = ImageFont.load_default()  


                text = "ТВОЕ ИДЕАЛЬНОЕ \nФОТО - НАШ ФОРМАТ"
                text_bbox = draw.textbbox((0, 0), text, font=font)
                text_width = text_bbox[2] - text_bbox[0]
                text_height = text_bbox[3] - text_bbox[1]
                text_position = (qr_position[0] + qr_image.width + 20, qr_position[1] + (qr_image.height - text_height) // 2)  


                draw.text(text_position, text, (0, 0, 0), font=font)


                buf = io.BytesIO()
                final_image.save(buf, format='PNG')
                byte_im = buf.getvalue()

                bot.send_document(message.chat.id, byte_im, caption="Спасибо за покупку! Вот ваше фото.", visible_file_name="ВашеФото.jpg")
            else:
                bot.send_message(message.chat.id, "Ошибка: не удалось получить URL фото.")
                logging.error("API не вернул printLayoutImage.")
        else:
            bot.send_message(message.chat.id, f"Ошибка при обработке фото: {response.status_code}")
            logging.error(f"Ошибка API: {response.status_code}, {response.text}")
    
        bot.send_message(message.chat.id, 'Операция завершена.', reply_markup=main_menu_keyboard())




    

def cancel_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton('Отмена'))
    return keyboard

@bot.message_handler(func=lambda message: message.text == 'Отмена')
def cancel_action(message):
    bot.send_message(message.chat.id, 'Операция отменена.', reply_markup=main_menu_keyboard())

app = Flask(__name__)

def start_flask():
    app.run(host='0.0.0.0', port=8000, debug=False)

from threading import Thread

if __name__ == "__main__":
    t = Thread(target=start_flask)
    t.start()
    bot.polling(none_stop=True)