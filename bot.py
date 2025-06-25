import os 
import telebot
from telebot import types

# اطلاعات جدید ربات 
TOKEN = os.getenv('BOT_TOKEN') # این خط رو جایگزین خط بالا کنید
CHANNEL_ID = 'CHANNEL_ID'
SUPPORT_ID = 'SUPPORT_ID'

bot = telebot.TeleBot(TOKEN)

# نیازی به verified_users نیست، چون هر بار عضویت چک می‌شود
# verified_users = set()

# بررسی عضویت در کانال
def is_user_member(user_id):
    try:
        status = bot.get_chat_member(CHANNEL_ID, user_id).status
        return status in ['member', 'administrator', 'creator']
    except Exception as e:
        # برای اشکال‌زدایی، می‌توانید خطای رخ داده را پرینت کنید
        # print(f"Error checking membership: {e}")
        return False

# فایل‌ها با کلید مخصوص
file_map = {
    'v1': 'arad_club_v1.1.exe',
    'v2': 'arad_club_v1.2.exe',
}

@bot.message_handler(commands=['start'])
def handle_start(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    args = message.text.split()
    tweak_key = args[1] if len(args) > 1 else None

    # همیشه در ابتدا عضویت را چک می‌کنیم
    if is_user_member(user_id):
        # اگر کاربر عضو بود، مستقیماً فایل را ارسال می‌کنیم
        bot.send_message(chat_id, "✅ عضویت شما تایید شد. در حال ارسال برنامه...")
        send_file_if_exists(chat_id, tweak_key)
    else:
        # اگر کاربر عضو نبود، پیام عضویت و دکمه‌ها را ارسال می‌کنیم
        text = "برای دریافت برنامه باید عضو کانال ما شوید.\nبعد از عضویت، روی «✅ تایید عضویت» بزنید."
        bot.send_message(chat_id, text, reply_markup=membership_markup(tweak_key))

def membership_markup(tweak_key=None):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📢 عضویت در کانال", url=f"https://t.me/{CHANNEL_ID.strip('@')}"))
    # callback_data باید شامل کلید باشد تا بعد از تایید عضویت، فایل درست ارسال شود
    markup.add(types.InlineKeyboardButton("✅ تایید عضویت", callback_data=f"check_{tweak_key if tweak_key else 'none'}"))
    markup.add(types.InlineKeyboardButton("📞 پشتیبانی", url=f"https://t.me/{SUPPORT_ID.strip('@')}"))
    return markup

@bot.callback_query_handler(func=lambda call: call.data.startswith("check_"))
def handle_callback(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    tweak_key = call.data.replace("check_", "") # استخراج کلید از callback_data

    if is_user_member(user_id):
        # اگر کاربر با دکمه "تایید عضویت" کلیک کرد و عضو بود
        bot.send_message(chat_id, "✅ عضویت شما تایید شد. در حال ارسال برنامه...")
        send_file_if_exists(chat_id, tweak_key)
    else:
        # اگر کاربر عضو نبود، بهش اطلاع می‌دهیم
        bot.answer_callback_query(call.id, "🚫 هنوز عضو کانال نیستید. لطفاً ابتدا عضو شوید.", show_alert=True)
        # می‌توانیم دوباره دکمه‌های عضویت را هم بفرستیم
        bot.send_message(chat_id, "برای دریافت برنامه باید عضو کانال ما شوید.\nبعد از عضویت، روی «✅ تایید عضویت» بزنید.", reply_markup=membership_markup(tweak_key))


def send_file_if_exists(chat_id, tweak_key):
    file_path = file_map.get(tweak_key)
    if file_path:
        try:
            with open(file_path, "rb") as f:
                bot.send_document(chat_id, f)
        except FileNotFoundError:
            bot.send_message(chat_id, "❌ فایل پیدا نشد. لطفاً با پشتیبانی تماس بگیرید.")
    else:
        bot.send_message(chat_id, "❗ لینک وارد شده اشتباه است یا فایلی برای آن وجود ندارد.")

bot.infinity_polling()
