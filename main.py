import requests
import time
import telebot
import threading
from lock import pas

bot = telebot.TeleBot(pas)

base_url = 'https://contract.mexc.com'

def get_all_prices():
    url = f"{base_url}/api/v1/contract/ticker"
    response = requests.get(url)
    if response.status_code == 200:
        return {item['symbol']: float(item['lastPrice']) for item in response.json()['data']}
    return {}

def price_tracker(chat_id, threshold=0.05, interval=10):
    initial_prices = get_all_prices()
    if not initial_prices:
        bot.send_message(chat_id, "try again ")
        return
    while True:
        time.sleep(interval)
        current_prices = get_all_prices()
        for symbol, old_price in initial_prices.items():
            if symbol == "JAGER_USDT":
                new_price = current_prices.get(symbol)
                if not new_price:
                    continue
                change = (new_price - old_price) / old_price
                if change >= threshold:
                    percent = round(change * 100, 2)
                    bot.send_message(chat_id, f"🟢 {symbol} is up by {percent}%")
                    initial_prices[symbol] = new_price
                elif change <= -threshold:
                    percent = round(abs(change) * 100, 2)
                    bot.send_message(chat_id, f"🔴 {symbol} plummeted by {percent}%")
                    initial_prices[symbol] = new_price

@bot.message_handler(commands=["start"])
def start_tracking(message):
    bot.send_message(message.chat.id, "futures tracking started")
    thread = threading.Thread(target=price_tracker, args=(message.chat.id,))
    thread.start()

bot.polling()
