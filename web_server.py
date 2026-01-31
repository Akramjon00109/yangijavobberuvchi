"""
Web Service runner for Render.com (Free Tier)
Runs Flask server with health check + bots in background threads
"""
import threading
import time
import os
from flask import Flask, jsonify

app = Flask(__name__)

# Global status
bot_status = {
    "instagram": "starting",
    "telegram": "starting",
    "started_at": None
}


@app.route("/")
def home():
    """Home page"""
    return """
    <html>
    <head><title>Instagram + Telegram Bot</title></head>
    <body style="font-family: Arial; text-align: center; padding: 50px;">
        <h1>🤖 Instagram + Telegram Bot</h1>
        <p>Bot ishlayapti!</p>
        <p><a href="/health">Health Check</a></p>
    </body>
    </html>
    """


@app.route("/health")
def health():
    """Health check endpoint for UptimeRobot"""
    return jsonify({
        "status": "ok",
        "instagram_bot": bot_status["instagram"],
        "telegram_bot": bot_status["telegram"],
        "started_at": bot_status["started_at"]
    })


def run_instagram_bot():
    """Run the Instagram comment bot"""
    global bot_status
    try:
        bot_status["instagram"] = "running"
        from main import main as instagram_main
        instagram_main()
    except Exception as e:
        bot_status["instagram"] = f"error: {str(e)}"
        print(f"❌ Instagram bot xatosi: {e}")


def run_telegram_bot():
    """Run the Telegram subscription bot"""
    global bot_status
    try:
        bot_status["telegram"] = "running"
        from telegram_bot import main as telegram_main
        telegram_main()
    except Exception as e:
        bot_status["telegram"] = f"error: {str(e)}"
        print(f"❌ Telegram bot xatosi: {e}")


def start_bots():
    """Start both bots in background threads"""
    global bot_status
    from datetime import datetime
    bot_status["started_at"] = datetime.now().isoformat()
    
    print("=" * 50)
    print("🤖 Instagram + Telegram Bot (Web Service)")
    print("=" * 50)
    
    # Start Instagram bot in a thread
    instagram_thread = threading.Thread(target=run_instagram_bot, daemon=True)
    instagram_thread.start()
    print("✅ Instagram bot ishga tushdi (background thread)")
    
    # Small delay before starting Telegram bot
    time.sleep(2)
    
    # Start Telegram bot in a thread
    telegram_thread = threading.Thread(target=run_telegram_bot, daemon=True)
    telegram_thread.start()
    print("✅ Telegram bot ishga tushdi (background thread)")


# Start bots when module loads
start_bots()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
