import os
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Filters, CallbackContext
import yt_dlp

TOKEN = os.environ.get("BOT_TOKEN")
bot = Bot(token=TOKEN)
app = Flask(__name__)

dispatcher = Dispatcher(bot=bot, update_queue=None, use_context=True)

def start(update: Update, context: CallbackContext):
    update.message.reply_text("Send a YouTube or Facebook video URL.")

def download_video(update: Update, context: CallbackContext):
    url = update.message.text
    update.message.reply_text("Downloading... Please wait.")

    try:
        ydl_opts = {
            'outtmpl': 'video.%(ext)s',
            'format': 'bestvideo+bestaudio/best',
            'merge_output_format': 'mp4',
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info).replace(".webm", ".mp4")

        with open(file_path, 'rb') as f:
            update.message.reply_video(video=f)

        os.remove(file_path)

    except Exception as e:
        update.message.reply_text(f"❌ Error: {str(e)}")

dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, download_video))

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return 'OK'

@app.route("/", methods=["GET"])
def index():
    return "Bot is running!"

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000)
