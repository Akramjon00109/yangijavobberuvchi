"""
Combined runner for both Instagram and Telegram bots
Use this for Render.com deployment
"""
import threading
import time
import sys


def run_instagram_bot():
    """Run the Instagram comment bot"""
    try:
        from main import main as instagram_main
        instagram_main()
    except Exception as e:
        print(f"❌ Instagram bot xatosi: {e}")


def run_telegram_bot():
    """Run the Telegram subscription bot"""
    try:
        from telegram_bot import main as telegram_main
        telegram_main()
    except Exception as e:
        print(f"❌ Telegram bot xatosi: {e}")


def main():
    print("=" * 50)
    print("🤖 Instagram + Telegram Bot Runner")
    print("=" * 50)
    
    # Start Instagram bot in a thread
    instagram_thread = threading.Thread(target=run_instagram_bot, daemon=True)
    instagram_thread.start()
    print("✅ Instagram bot ishga tushdi")
    
    # Small delay before starting Telegram bot
    time.sleep(2)
    
    # Start Telegram bot in main thread (it has its own event loop)
    print("✅ Telegram bot ishga tushdi")
    run_telegram_bot()


if __name__ == "__main__":
    main()
