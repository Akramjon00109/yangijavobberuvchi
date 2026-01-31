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
    import sys
    
    # Force unbuffered output
    sys.stdout.reconfigure(line_buffering=True)
    
    try:
        print("🔄 Instagram bot yuklanmoqda...", flush=True)
        bot_status["instagram"] = "loading"
        
        from main import main as instagram_main
        print("✅ Instagram bot moduli yuklandi", flush=True)
        
        bot_status["instagram"] = "running"
        instagram_main()
    except Exception as e:
        import traceback
        error_msg = f"error: {str(e)}"
        bot_status["instagram"] = error_msg
        print(f"❌ Instagram bot xatosi: {e}", flush=True)
        print(traceback.format_exc(), flush=True)


def run_telegram_bot():
    """Run the Telegram subscription bot with its own event loop"""
    global bot_status
    import asyncio
    import sys
    
    sys.stdout.reconfigure(line_buffering=True)
    
    try:
        print("🔄 Telegram bot yuklanmoqda...", flush=True)
        
        # Create new event loop for this thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        bot_status["telegram"] = "running"
        from telegram_bot import TelegramSubscriptionBot
        bot = TelegramSubscriptionBot()
        print("✅ Telegram bot moduli yuklandi", flush=True)
        bot.run(use_signals=False)  # Disable signals for threaded mode
    except Exception as e:
        import traceback
        bot_status["telegram"] = f"error: {str(e)}"
        print(f"❌ Telegram bot xatosi: {e}", flush=True)
        print(traceback.format_exc(), flush=True)


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
