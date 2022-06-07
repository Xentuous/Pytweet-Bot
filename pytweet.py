import os 
import logging
import tweepy

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackContext

load_dotenv()
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

STARTED = False

# Initialise the application
def init():
    app = ApplicationBuilder().token(os.getenv('TOKEN')).build()
    return app

def get_client():
    client = tweepy.Client(consumer_key=os.getenv('CONSUMER_KEY'), consumer_secret=os.getenv('CONSUMER_SECRET'), access_token=os.getenv('ACCESS_TOKEN'), access_token_secret=os.getenv('ACCESS_SECRET'))
    return client

# Handles list of command
def dispatch_handler(app: ApplicationBuilder):
    app.add_handler(CommandHandler("start", begin))
    app.add_handler(CommandHandler("tweet", tweet))

# Start command
async def begin(update: Update, context: CallbackContext.DEFAULT_TYPE):
    text = "Hello! I am a bot that tweets your message!\nSimply type /tweet <message> to tweet your message!"
    await context.bot.send_message(chat_id=update.effective_chat.id,text=text)
    
async def tweet(update: Update, context: CallbackContext.DEFAULT_TYPE):
    client = get_client()
    
    try:
        tweet = update.message.text
        tweet = tweet[6:]

        if len(tweet) > 140:
            i = 1
            list_of_tweets = []
            
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Your tweet exceeds 140 characters, it will be split into multiple tweets!")

            while len(tweet) > 140:
                list_of_tweets.append("(" + str(i) + ") " + tweet[:136])
                tweet = tweet[136:]
                i += 1

            list_of_tweets.append("(" + str(i) + ") " + tweet)

            for tweet in list_of_tweets:
                await update.message.reply_text("You have tweeted: " + tweet)
                response = client.create_tweet(text=tweet)
                logging.info(f"Chat id: {update.effective_chat.id}, tweeted: {response}")
        else:
            await update.message.reply_text("You have tweeted: " + tweet)
            response = client.create_tweet(text=tweet)
            await update.message.reply_text("Your tweet has been sent!")
            logging.info(f"Chat id: {update.effective_chat.id}, tweeted: {response}")

    except Exception as e:
        logging.error(f"Error: {e}")

def main():
    app = init()
    dispatch_handler(app)
    app.run_polling()

if __name__ == '__main__':
    main()
