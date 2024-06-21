import subprocess
from database import db_check_running

bot_process = None

def start_bot():
    global bot_process
    discord_bot_script = "bot.py"
    bot_process = subprocess.Popen(['python', discord_bot_script])

def stop_bot():
    global bot_process
    if bot_process:
        bot_process.terminate()
        bot_process = None
        print("Bot has been stopped.")
    else:
        print("Bot is not currently running.")

stop_bot()