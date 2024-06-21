from telegram import *
from telegram.ext import *
from util import YamlFile
from spotify import Spotify

from youtube import *


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Hi! I am downloading songs from Spotify. "
                                                                          "Just send me a link and I will provide "
                                                                          "you with MP3's!")


async def download_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    client = context.bot_data['spotify_client']
    tracks = client.get_tracks(update.message.text)

    if tracks:
        context.job_queue.run_once(download_job, 0, data={'chat_id': update.effective_chat.id,
                                                          'message_id': update.message.id,
                                                          'tracks': tracks})
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       reply_to_message_id=update.message.id, text=f'Working on it!')
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f'Could not resolve your link.')


async def download_job(context: CallbackContext):

    data = context.job.data

    chat = data['chat_id']
    msg = data['message_id']
    tracks = data['tracks']

    files = await download_tracks(tracks)

    for file in files:
        if file and os.path.getsize(file) > 0:
            await context.bot.send_audio(chat_id=chat, audio=open(file, 'rb'), reply_to_message_id=msg)
            os.remove(file)
        else:
            print(f"File {file} is empty or failed to download.")

    await context.bot.send_message(chat_id=chat, reply_to_message_id=msg, text=f'Download complete!')



def main():

    config = YamlFile('config.yaml')  # data from cfg

    application = ApplicationBuilder().token(config.telegram_token).build()

    client = Spotify(config.spotify_client_id, config.spotify_client_secret)
    application.bot_data['spotify_client'] = client  # storing an instance of spotify connection for access

    add_handlers(application)
    application.run_polling()


def add_handlers(application):

    start_handler = CommandHandler('start', start)
    download_handler = MessageHandler(filters.TEXT, download_message)
    application.add_handler(start_handler)
    application.add_handler(download_handler)


if __name__ == '__main__':
    main()
