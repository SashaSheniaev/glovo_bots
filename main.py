import telebot
from telebot import types
import random
import time

TOKEN = '7858930235:AAGPKmIOtYmkj8gKQYlLiWCaoRsCQEyifRw='
bot = telebot.TeleBot(TOKEN)

products = []
cart = {}
returns = []

def get_main_keyboard():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(
        types.KeyboardButton('Команди'),
        types.KeyboardButton('Додати товар'),
        types.KeyboardButton('Товари'),
        types.KeyboardButton('Кошик'),
        types.KeyboardButton('Оплата'),
        types.KeyboardButton('Повернути товар'),
    )
    return markup

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = (
        "Вітаємо у боті!\n\n"
        "Використовуйте кнопки нижче для роботи з ботом.\n\n"
        "Доступні команди:\n"
        "Команди\n"
        "Додати товар\n"
        "Товари\n"
        "Кошик\n"
        "Оплатити\n"
        "Повернути товар"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=get_main_keyboard())

@bot.message_handler(func=lambda message: message.text == 'Товари')
def show_products(message):
    show_list = [
        {'name': 'Картопля фрі', 'price': 200},
        {'name': 'Кола 0.5л', 'price': 100},
        {'name': 'Шефбургер', 'price': 90},
        {'name': 'Гострі крильця', 'price': 150},
        {'name': 'Морозиво', 'price': 80},
        {'name': 'Твістер чіз', 'price': 120},
        {'name': 'Соус кислосолодкий', 'price': 20},
        {'name': 'Соус барьекю', 'price': 20},
        {'name': 'Соус сирний', 'price': 20},
        {'name': 'Картоаляні діпи', 'price': 60},
        {'name': 'Печиво з шоколадом', 'price': 50}
    ]
    
    products_text = "📋 Наші товари:\n\n"
    for item in show_list:
        products_text += f"🍽 {item['name']} - {item['price']} грн\n"
    
    bot.send_message(message.chat.id, products_text, reply_markup=get_main_keyboard())
    global products
    products = show_list

@bot.message_handler(func=lambda message: message.text == 'Додати товар')
def add_to_cart_start(message):
    if not products:
        bot.send_message(message.chat.id, "Спочатку перегляньте список товарів!", reply_markup=get_main_keyboard())
        return
    
    products_text = "Виберіть товар для додавання в кошик:\n\n"
    for i, item in enumerate(products, 1):
        products_text += f"{i}. {item['name']} - {item['price']} грн\n"
    
    msg = bot.send_message(message.chat.id, products_text)
    bot.register_next_step_handler(msg, process_product_selection)

def process_product_selection(message):
    try:
        choice = int(message.text)
        if 1 <= choice <= len(products):
            selected_product = products[choice - 1]
            user_id = message.from_user.id
            
            if user_id not in cart:
                cart[user_id] = []
            
            cart[user_id].append(selected_product)
            bot.send_message(
                message.chat.id,
                f"✅ Товар '{selected_product['name']}' додано до кошика!",
                reply_markup=get_main_keyboard()
            )
        else:
            bot.send_message(
                message.chat.id,
                "❌ Неправильний вибір. Спробуйте ще раз.",
                reply_markup=get_main_keyboard()
            )
    except ValueError:
        bot.send_message(
            message.chat.id,
            "❌ Будь ласка, введіть номер товару.",
            reply_markup=get_main_keyboard()
        )

@bot.message_handler(func=lambda message: message.text == 'Кошик')
def show_cart(message):
    user_id = message.from_user.id
    if user_id not in cart or not cart[user_id]:
        bot.send_message(message.chat.id, "Ваш кошик порожній!", reply_markup=get_main_keyboard())
        return
    
    cart_text = "🛒 Ваш кошик:\n\n"
    total = 0
    for item in cart[user_id]:
        cart_text += f"🍽 {item['name']} - {item['price']} грн\n"
        total += item['price']
    
    cart_text += f"\n💵 Загальна сума: {total} грн"
    bot.send_message(message.chat.id, cart_text, reply_markup=get_main_keyboard())