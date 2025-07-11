import telebot
from telebot import types
import random
import time

# Get your token from @BotFather and paste it here
TOKEN = '7676646213:AAG46iCXoDDCbyVqdfVNtz10JnRchXlbvnk'  # Replace this with your new token from @BotFather
bot = telebot.TeleBot(TOKEN)

products = []
cart = {}
returns = {}
user_payment_data = {}
user_payment_step = {}

def get_main_keyboard():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(
        types.KeyboardButton('Команди'),
        types.KeyboardButton('Додати товар'),
        types.KeyboardButton('Товари'),
        types.KeyboardButton('Кошик'),
        types.KeyboardButton('Оплатити'),
        types.KeyboardButton('Повернути товар'),
    )
    return markup

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = (
        "Вітаємо у боті!\n\n"
        "Використовуйте кнопки нижче для роботи з ботом.\n\n"
        "Доступні команди:\n"
        "Команди — показати це меню\n"
        "Додати товар — додати товар у кошик\n"
        "Товари — переглянути список товарів\n"
        "Кошик — переглянути вміст кошика\n"
        "Оплатити — оформити оплату\n"
        "Повернути товар — повернути товар з кошика"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=get_main_keyboard())

@bot.message_handler(func=lambda message: message.text == 'Команди')
def show_commands(message):
    send_welcome(message)

@bot.message_handler(func=lambda message: message.text == 'Товари')
def show_products(message):
    global products
    show_list = [
        {'name': 'Картопля фрі', 'price': 200},
        {'name': 'Кола 0.5л', 'price': 100},
        {'name': 'Шефбургер', 'price': 90},
        {'name': 'Гострі крильця', 'price': 150},
        {'name': 'Морозиво', 'price': 80},
        {'name': 'Твістер чіз', 'price': 120},
        {'name': 'Соус кислосолодкий', 'price': 20},
        {'name': 'Соус барбекю', 'price': 20},
        {'name': 'Соус сирний', 'price': 20},
        {'name': 'Картопляні діпи', 'price': 60},
        {'name': 'Печиво з шоколадом', 'price': 50}
    ]
    products_text = "📋 Наші товари:\n\n"
    for item in show_list:
        products_text += f"🍽 {item['name']} - {item['price']} грн\n"
    products = show_list
    bot.send_message(message.chat.id, products_text, reply_markup=get_main_keyboard())

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
    if message.content_type != 'text':
        bot.send_message(message.chat.id, "Будь ласка, введіть номер товару текстом.")
        bot.register_next_step_handler(message, process_product_selection)
        return
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

@bot.message_handler(func=lambda message: message.text == 'Оплатити')
def process_payment(message):
    user_id = message.from_user.id
    if user_id not in cart or not cart[user_id]:
        bot.send_message(message.chat.id, "Немає товарів для оплати. Ваш кошик порожній!", reply_markup=get_main_keyboard())
        return
    bot.send_message(message.chat.id, "Вкажіть адресу доставки:")
    bot.register_next_step_handler(message, get_address_for_payment)

def get_address_for_payment(message):
    user_id = message.from_user.id
    if message.content_type != 'text':
        bot.send_message(message.chat.id, "Будь ласка, введіть адресу текстом.")
        bot.register_next_step_handler(message, get_address_for_payment)
        return
    address = message.text.strip()
    if not address:
        bot.send_message(message.chat.id, "❌ Адреса не може бути порожньою. Вкажіть адресу доставки:")
        bot.register_next_step_handler(message, get_address_for_payment)
        return
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton('Оплата карткою', callback_data='pay_card'),
        types.InlineKeyboardButton('Оплата готівкою', callback_data='pay_cash')
    )
    bot.send_message(message.chat.id, 'Оберіть спосіб оплати', reply_markup=markup)
    user_payment_data[user_id] = {'address': address}

@bot.callback_query_handler(func=lambda call: call.data == 'pay_card')
def process_card_payment(call):
    user_id = call.from_user.id
    user_payment_step[user_id] = 'card_number'
    bot.send_message(call.message.chat.id, 'Введіть номер картки (ліміт 16 цифр):')
    bot.register_next_step_handler(call.message, get_card_number)

def get_card_number(message):
    user_id = message.from_user.id
    if message.content_type != 'text':
        bot.send_message(message.chat.id, "Будь ласка, введіть номер картки текстом.")
        bot.register_next_step_handler(message, get_card_number)
        return
    card_number = message.text.strip()
    if not card_number.isdigit() or len(card_number) != 16:
        bot.send_message(message.chat.id, '❌ Невірний номер картки. Спробуйте ще раз (16 цифр):')
        bot.register_next_step_handler(message, get_card_number)
        return
    user_payment_data[user_id]['card_number'] = card_number
    bot.send_message(message.chat.id, 'Введіть CVV (3 цифри):')
    bot.register_next_step_handler(message, get_card_cvv)

def get_card_cvv(message):
    user_id = message.from_user.id
    if message.content_type != 'text':
        bot.send_message(message.chat.id, "Будь ласка, введіть CVV текстом.")
        bot.register_next_step_handler(message, get_card_cvv)
        return
    cvv = message.text.strip()
    if not cvv.isdigit() or len(cvv) != 3:
        bot.send_message(message.chat.id, '❌ Невірний CVV. Спробуйте ще раз (3 цифри):')
        bot.register_next_step_handler(message, get_card_cvv)
        return
    user_payment_data[user_id]['cvv'] = cvv
    bot.send_message(message.chat.id, 'Введіть рік закінчення дії картки (наприклад, 2025):')
    bot.register_next_step_handler(message, get_card_expiry)

def get_card_expiry(message):
    user_id = message.from_user.id
    if message.content_type != 'text':
        bot.send_message(message.chat.id, "Будь ласка, введіть рік текстом.")
        bot.register_next_step_handler(message, get_card_expiry)
        return
    year = message.text.strip()
    if not year.isdigit() or len(year) != 4 or int(year) < 2024:
        bot.send_message(message.chat.id, '❌ Невірний рік. Спробуйте ще раз (наприклад, 2025):')
        bot.register_next_step_handler(message, get_card_expiry)
        return
    user_payment_data[user_id]['expiry_year'] = year
    bot.send_message(message.chat.id, '✅ Оплата карткою успішно завершена! Дякуємо за покупку.', reply_markup=get_main_keyboard())
    if user_id in cart:
        cart[user_id] = []
    if user_id in user_payment_step:
        del user_payment_step[user_id]
    if user_id in user_payment_data:
        del user_payment_data[user_id]
    if user_id in returns:
        returns[user_id] = []

@bot.callback_query_handler(func=lambda call: call.data == 'pay_cash')
def process_cash_payment(call):
    user_id = call.from_user.id
    bot.send_message(call.message.chat.id, '✅ Замовлення прийнято! Оплата готівкою при отриманні. Дякуємо за покупку.', reply_markup=get_main_keyboard())
    if user_id in cart:
        cart[user_id] = []
    if user_id in user_payment_step:
        del user_payment_step[user_id]
    if user_id in user_payment_data:
        del user_payment_data[user_id]
    if user_id in returns:
        returns[user_id] = []

@bot.message_handler(func=lambda message: message.text == 'Повернути товар')
def return_item_start(message):
    user_id = message.from_user.id
    if user_id not in cart or not cart[user_id]:
        bot.send_message(message.chat.id, "Немає товарів для повернення. Ваш кошик порожній!", reply_markup=get_main_keyboard())
        return
    return_text = "Виберіть товар для повернення:\n\n"
    for i, item in enumerate(cart[user_id], 1):
        return_text += f"{i}. {item['name']} - {item['price']} грн\n"
    msg = bot.send_message(message.chat.id, return_text)
    bot.register_next_step_handler(msg, process_return_selection)

def process_return_selection(message):
    user_id = message.from_user.id
    if message.content_type != 'text':
        bot.send_message(message.chat.id, "Будь ласка, введіть номер товару текстом.")
        bot.register_next_step_handler(message, process_return_selection)
        return
    try:
        choice = int(message.text)
        if 1 <= choice <= len(cart[user_id]):
            returned = cart[user_id].pop(choice - 1)
            if user_id not in returns:
                returns[user_id] = []
            returns[user_id].append(returned)
            bot.send_message(
                message.chat.id,
                f"✅ Товар '{returned['name']}' успішно повернено!",
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

@bot.message_handler(content_types=['photo', 'animation'])
def ignore_media(message):
    bot.send_message(message.chat.id, "Будь ласка, надсилайте текстове повідомлення, а не медіа.")

if __name__ == '__main__':
    print("Bot started...")
    while True:
        try:
            bot.polling(none_stop=True, interval=0)
        except Exception as e:
            print(f"Error occurred: {e}")
            time.sleep(15)

