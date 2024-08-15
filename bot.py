import telebot
from telebot import types
from Hero import heroes_dict
from main import get_dota2_market_items

bot = telebot.TeleBot('6424631446:AAHb0vvDHJa9sej7weVLktGzpmc1hNTBbBA')


def send_greeting(message):
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    if last_name is None:
        bot.send_message(message.chat.id,
                         f'Hello, {first_name}! This bot is able to issue items from the Steam Community Market for Dota 2 games, which can bring profit if the quality changes.')
    else:
        bot.send_message(message.chat.id,
                         f'Hello, {first_name} {last_name}! This bot is able to issue items from the Steam Community Market for Dota 2 games, which can bring profit if the quality changes.')


@bot.message_handler(commands=['start'])
def handle_start(message):
    send_greeting(message)


@bot.message_handler(commands=['help'])
def handle_help(message):
    help_text = (
        "This bot provides information about Dota 2 items available on the Steam Community Market.\n\n"
        "To use this bot, you can follow these steps:\n"
        "1. Use the /hero command to select a Dota 2 hero.\n"
        "2. Once a hero is selected, the bot will display a list of items related to that hero from the Steam Community Market.\n"
        "3. You can navigate through the items using the 'Next page' button.\n\n"
        "Note: The items displayed may bring profit if their price changes over time. The profit is calculated based on the difference between the current market price and the original price."
    )
    bot.send_message(message.chat.id, help_text)


@bot.message_handler(commands=['hero'])
def handle_hero_command(message):
    keyboard = generate_hero_keyboard()
    bot.send_message(message.chat.id, 'Select a hero:', reply_markup=keyboard)


def generate_hero_keyboard():
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    buttons = [types.KeyboardButton(hero) for hero in heroes_dict.keys()]
    keyboard.add(*buttons)
    return keyboard


current_page = 1


@bot.message_handler(func=lambda message: message.text in heroes_dict.keys())
def handle_selected_hero(message):
    global current_page
    hero_name = message.text
    results = get_dota2_market_items(heroes_dict[hero_name], page=current_page)
    if results:
        for result in results:
            item_name = result['name']
            item_price = result['price']
            item_href = result['href']
            item_profit = result.get('profit', 'N/A')  # If 'profit' is missing, set it to 'N/A'
            message_text = f"Name: {item_name}\nPrice: {item_price}\nProfit: {item_profit}\nLink: {item_href}"
            bot.send_message(message.chat.id, message_text)
    else:
        bot.send_message(message.chat.id, "No items found for this hero.")

    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    next_page_button = types.KeyboardButton("Next page")
    keyboard.add(next_page_button)
    bot.send_message(message.chat.id, "Press the button to go to the next page.", reply_markup=keyboard)


@bot.message_handler(func=lambda message: message.text == "Next page")
def handle_next_page(message):
    global current_page
    current_page += 1
    handle_selected_hero(message)


bot.infinity_polling()
